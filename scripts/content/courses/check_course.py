"""Runs every code sample of the test questions with the real compiler or interpreter and compares the output
with the marked answer.

    python3 scripts/content/courses/check_course.py <folder> [--show]

Fragments are wrapped into a program (main function, imports) here only; learners see the fragment. A question is
checked when its text starts with «Что выведет» (output) or its answer starts with «Ошибка компиляции» (the code
must not compile).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = '/opt/go1.25.2/bin:/opt/node22/bin:/usr/local/bin:/usr/bin:/bin'
ENV = {'PATH': PATH, 'HOME': '/tmp', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'PYTHONIOENCODING': 'utf-8', 'DOTNET_CLI_TELEMETRY_OPTOUT': '1',
       'DOTNET_NOLOGO': '1', 'GOCACHE': '/tmp/gocache', 'GOFLAGS': '-mod=mod', 'GOPATH': '/tmp/gopath'}


def load(folder):
    base = {}
    with open(os.path.join(HERE, '_dsl.py'), encoding='utf-8') as f:
        exec(compile(f.read(), '_dsl.py', 'exec'), base)
    meta = dict(base)
    with open(os.path.join(folder, 'course.py'), encoding='utf-8') as f:
        exec(compile(f.read(), 'course.py', 'exec'), meta)
    modules = []
    for name in sorted(os.listdir(folder)):
        if re.fullmatch(r'm[0-9]+\.py', name):
            scope = dict(base)
            with open(os.path.join(folder, name), encoding='utf-8') as f:
                exec(compile(f.read(), name, 'exec'), scope)
            modules.append((name, scope['MODULE']))
    return meta['META'], modules


def sh(cmd, cwd, timeout=60):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=timeout, env=ENV)
    return p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')


def write(tmp, name, text):
    path = os.path.join(tmp, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    return path


GO_IMPORTS = {'strings': 'strings.', 'strconv': 'strconv.', 'math': 'math.', 'sort': 'sort.', 'os': 'os.',
              'errors': 'errors.', 'time': 'time.', 'sync': 'sync.', 'bufio': 'bufio.', 'unicode': 'unicode.', 'slices': 'slices.', 'maps': 'maps.', 'context': 'context.'}


def run_go(code, tmp):
    imports = ['fmt'] + [name for name, use in GO_IMPORTS.items() if use in code and '"%s"' % name not in code]
    head = 'package main\n\nimport (\n%s\n)\n\n' % '\n'.join('\t"%s"' % i for i in imports)
    if 'func main' not in code:
        code = head + 'func main() {\n%s\n}\n' % code
    elif 'package main' not in code:
        code = head + code
    write(tmp, 'main.go', code)
    write(tmp, 'go.mod', 'module x\n\ngo 1.25\n')
    result = sh(['go', 'run', '.'], tmp, 120)
    if result[0] != 0 and re.search(r'main[.]go:[0-9]+:[0-9]+:', result[2]) and 'goroutine' not in result[2]:
        return 'compile', result[1], result[2]
    return result


def run_cpp(code, tmp):
    if 'int main' not in code:
        code = '#include <bits/stdc++.h>\nusing namespace std;\nint main() {\n%s\nreturn 0;\n}\n' % code
    elif '#include' not in code:
        code = '#include <bits/stdc++.h>\nusing namespace std;\n' + code
    write(tmp, 'a.cpp', code)
    c, out, err = sh(['g++', '-std=c++20', '-O0', '-o', 'a.out', 'a.cpp'], tmp, 120)
    if c != 0:
        return 'compile', out, err
    return sh(['./a.out'], tmp)


def run_java(code, tmp):
    if 'static void main' not in code:
        code = ('import java.util.*;\nimport java.util.function.*;\nimport java.util.stream.*;\n'
                'public class Main {\npublic static void main(String[] args) throws Exception {\n%s\n}\n}\n' % code)
    elif 'import ' not in code:
        code = 'import java.util.*;\nimport java.util.function.*;\nimport java.util.stream.*;\n' + code
    name = 'Main'
    found = re.search(r'public\s+(?:final\s+)?class\s+(\w+)', code)
    if found:
        name = found.group(1)
    write(tmp, name + '.java', code)
    c, out, err = sh(['javac', '-encoding', 'UTF-8', name + '.java'], tmp, 120)
    if c != 0:
        return 'compile', out, err
    return sh(['java', '-Dfile.encoding=UTF-8', '-Dstdout.encoding=UTF-8', name], tmp)


CS_USINGS = ('using System;\nusing System.Collections.Generic;\nusing System.Linq;\nusing System.Text;\n'
             'using System.Threading;\nusing System.Threading.Tasks;\n')


def run_csharp(code, tmp):
    if 'static void Main' not in code and 'static int Main' not in code and 'static async Task Main' not in code:
        code = CS_USINGS + 'class Program\n{\nstatic void Main()\n{\n%s\n}\n}\n' % code
    elif 'using ' not in code:
        code = CS_USINGS + code
    write(tmp, 'a.cs', code)
    c, out, err = sh(['mcs', '-out:a.exe', 'a.cs'], tmp, 120)
    if c != 0:
        return 'compile', out, err
    return sh(['mono', 'a.exe'], tmp)


def run_js(code, tmp):
    write(tmp, 'a.js', code)
    return sh(['node', 'a.js'], tmp)


def run_python(code, tmp):
    write(tmp, 'a.py', code)
    return sh(['python3', '-I', 'a.py'], tmp)


RUNNERS = {'go': run_go, 'cpp': run_cpp, 'java': run_java, 'csharp': run_csharp, 'javascript': run_js,
           'python': run_python}


def main(name, show):
    folder = os.path.join(HERE, name)
    meta, modules = load(folder)
    run = RUNNERS[meta.get('lang', 'python')]
    bad = total = checked = 0
    for fname, module in modules:
        for lesson in module['lessons']:
            for block in lesson['blocks']:
                if block['type'] != 'test':
                    continue
                for n, q in enumerate(block['questions'], 1):
                    where = '%s q%d' % (fname, n)
                    kind = q.get('type', 'single')
                    opts = q['options']
                    total += 1
                    if len(set(opts)) != len(opts):
                        print('DUPLICATE OPTIONS', where)
                        bad += 1
                    if kind in ('single', 'multi'):
                        ans = q['answer'] if isinstance(q['answer'], list) else [q['answer']]
                        if any(not 0 <= a < len(opts) for a in ans):
                            print('BAD ANSWER INDEX', where)
                            bad += 1
                    if not q.get('code') or kind != 'single':
                        continue
                    right = opts[q['answer']]
                    wants_output = q['text'].startswith('Что выведет')
                    wants_error = right.startswith('Ошибка компиляции')
                    if not (wants_output or wants_error):
                        continue
                    checked += 1
                    tmp = tempfile.mkdtemp()
                    try:
                        code, out, err = run(q['code'], tmp)
                    except subprocess.TimeoutExpired:
                        print('TIMEOUT', where)
                        bad += 1
                        continue
                    finally:
                        shutil.rmtree(tmp, ignore_errors=True)
                    if wants_error:
                        if code != 'compile':
                            print('SHOULD NOT COMPILE', where, repr(out[:80]))
                            bad += 1
                        continue
                    if code != 0:
                        if not right.startswith('Ошибка') and 'Исключение' not in right and 'panic' not in right:
                            print('FAILED TO RUN', where, (err or out).strip()[:300].replace('\n', ' | '))
                            bad += 1
                        continue
                    got = out[:-1] if out.endswith('\n') else out
                    if got != right:
                        print('MISMATCH', where, 'got %r, marked %r' % (got, right))
                        if show:
                            print('   options:', opts)
                        bad += 1
    print('%s: questions %d, run %d, problems %d' % (name, total, checked, bad))
    return bad


if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1], '--show' in sys.argv) else 0)
