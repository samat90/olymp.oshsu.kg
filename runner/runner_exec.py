"""Compiling and running user code with the judge's executors.

Runs inside worker processes (see server.py). A program may consist of several
files: the main file plus helpers next to it (headers and .cpp files for C/C++,
classes for Java, modules for Python). Other languages use the main file only.
"""
import logging
import os
import re
import subprocess
import time

from runner_clean import clean

log = logging.getLogger('runner')

MAX_OUTPUT = 65536
MAX_FILES = 30
MAX_TOTAL_SOURCE = 256 * 1024
NAME_RE = re.compile(r'^[A-Za-z0-9_.\-]{1,100}$')

C_SOURCES = ('.c', '.cpp', '.cc', '.cxx')
C_HEADERS = ('.h', '.hpp', '.hh', '.hxx', '.inc')
C_LIKE = ('C', 'C11', 'CPP03', 'CPP11', 'CPP14', 'CPP17', 'CPP20', 'CPP23', 'CLANG', 'CLANGX')
JAVA_LIKE = ('JAVA', 'JAVA8', 'JAVA11', 'JAVA17', 'JAVA21')
PYTHON_LIKE = ('PY3', 'PY2', 'PYPY', 'PYPY3')


class RunnerError(Exception):
    pass


def clean_files(files, main):
    """{name: text} from the client -> {name: bytes}; flat names only."""
    if not isinstance(files, dict):
        files = {}
    out = {}
    total = 0
    for name, text in list(files.items())[:MAX_FILES]:
        name = os.path.basename(str(name))
        if not NAME_RE.match(name) or name in ('.', '..') or name == main:
            continue
        data = str(text).encode('utf-8')
        total += len(data)
        if total > MAX_TOTAL_SOURCE:
            raise RunnerError('Файлы проекта больше 256 КБ.')
        out[name] = data
    return out


def helper_files(language, extra):
    """Which extra files make sense for this language."""
    if language in C_LIKE:
        return {n: d for n, d in extra.items() if n.lower().endswith(C_SOURCES + C_HEADERS)}
    if language in JAVA_LIKE:
        return {n: d for n, d in extra.items() if n.endswith('.java')}
    if language in PYTHON_LIKE:
        return {n: d for n, d in extra.items() if n.endswith('.py') or not n.endswith(('.java', '.cpp', '.c'))}
    return {}


def build_executor(language, source, extra=None, unbuffered=False, cached=True):
    """Compiles (if needed) and returns a DMOJ executor. Raises CompileError."""
    from dmoj import executors
    from dmoj.executors.c_like_executor import CLikeExecutor
    from dmoj.executors.compiled_executor import CompiledExecutor

    if language not in executors.executors:
        raise RunnerError('Этот язык сейчас недоступен.')
    base = executors.executors[language].Executor
    extra = helper_files(language, extra or {})
    kwargs = {'unbuffered': unbuffered}

    if extra:
        cls = _with_extra_files(base, extra)
        if issubclass(base, CLikeExecutor):
            kwargs['aux_sources'] = {n: d for n, d in extra.items() if n.lower().endswith(C_SOURCES)}
    else:
        cls = base
    # The compile cache is keyed by the main source only, so it is safe only for single files.
    if cached and not extra and issubclass(base, CompiledExecutor):
        kwargs['cached'] = True
    return cls('main', source.encode('utf-8'), **kwargs)


def _with_extra_files(base, extra):
    from dmoj.executors.c_like_executor import CLikeExecutor

    class WithExtraFiles(base):
        def create_files(self, problem_id, source_code, *args, **kwargs):
            super().create_files(problem_id, source_code, *args, **kwargs)
            for name, data in extra.items():
                with open(self._file(name), 'wb') as f:
                    f.write(data)
            if isinstance(self, CLikeExecutor):
                # Headers are only included, never passed to the compiler.
                self.source_paths = [p for p in self.source_paths if p.lower().endswith(C_SOURCES)]

        def get_compile_args(self):
            args = super().get_compile_args()
            if str(getattr(self, '_code', '') or '').endswith('.java'):
                args = args + [self._file(n) for n in extra if n.endswith('.java')]
            return args

    WithExtraFiles.__name__ = base.__name__
    WithExtraFiles.__module__ = base.__module__
    return WithExtraFiles


def run_job(language, source, extra, stdins, args, time_limit, memory_limit):
    """Executed in a worker process. Compiles once and runs the program on every input."""
    from dmoj.error import CompileError

    started = time.monotonic()
    try:
        executor = build_executor(language, source, extra)
    except RunnerError as e:
        return {'status': 'error', 'message': str(e)}
    except CompileError as e:
        return {'status': 'compile_error', 'compile_output': clean(e.message)[:MAX_OUTPUT]}
    except Exception as e:  # compiler crashed, timed out, etc.
        log.exception('compile failed')
        return {'status': 'compile_error', 'compile_output': clean(str(e))[:MAX_OUTPUT]}
    compile_time = time.monotonic() - started
    warning = getattr(executor, 'warning', None) or b''
    if isinstance(warning, bytes):
        warning = warning.decode('utf-8', 'replace')

    runs = [run_once(executor, stdin, args, time_limit, memory_limit) for stdin in stdins]
    result = dict(runs[0])
    result['compile_time'] = round(compile_time, 2)
    result['compile_output'] = clean(warning)[:MAX_OUTPUT]
    if len(runs) > 1:
        result['runs'] = runs
    return result


def verdict_of(proc, ole=False):
    if proc.is_tle:
        return 'TLE'
    if proc.is_mle:
        return 'MLE'
    if ole or proc.is_ole:
        return 'OLE'
    if proc.returncode != 0:
        return 'RTE'
    return 'OK'


def run_once(executor, stdin, args, time_limit, memory_limit):
    from dmoj.utils.communicate import safe_communicate, OutputLimitExceeded

    proc = executor.launch(*args, time=time_limit, memory=memory_limit, wall_time=time_limit * 3 + 1,
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = safe_communicate(proc, stdin.encode('utf-8'), outlimit=MAX_OUTPUT, errlimit=MAX_OUTPUT)
        ole = False
    except OutputLimitExceeded:
        proc.kill()
        proc.wait()
        stdout, stderr, ole = b'', b'', True

    result = {
        'status': 'ok',
        'verdict': verdict_of(proc, ole),
        'stdout': stdout.decode('utf-8', 'replace'),
        'stderr': clean(stderr.decode('utf-8', 'replace')),
        'exit_code': proc.returncode,
        'time': round(proc.execution_time or 0, 3),
        'memory': proc.max_memory,
    }
    if proc.protection_fault:
        result['stderr'] += '\n[заблокирован системный вызов: %s]' % proc.protection_fault[1]
    return result
