#!/usr/bin/env python3
"""Code runner for the in-browser editor ("Запуск" button and the sandbox).

Runs next to the judge and uses the judge's own executors, so the editor
supports exactly the languages (and compilers, and sandbox) used for grading.

The site signs a short-lived token for the logged-in user; the browser sends
it with the code. The runner never talks to the database.

    python runner/server.py --config /home/judge/judge-config/judge.yml \
        --listen 127.0.0.1:9910 --secret-file /home/judge/runner.secret
"""
import argparse
import base64
import hashlib
import hmac
import json
import logging
import os
import subprocess
import sys
import threading
import time
from collections import defaultdict, deque
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FutureTimeout
from concurrent.futures.process import BrokenProcessPool
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import multiprocessing

log = logging.getLogger('runner')

MAX_SOURCE = 65536
MAX_STDIN = 1 << 20
MAX_OUTPUT = 65536
MAX_TIME = 5.0          # CPU seconds for the program itself
MAX_MEMORY = 262144     # KB
DEFAULT_TIME = 2.0
DEFAULT_MEMORY = 262144


def load_judge(config, only):
    argv = ['dmoj-runner', '-c', config, '--no-ansi', '--skip-self-test']
    if only:
        argv += ['-e', only]
    sys.argv = argv
    from dmoj import judgeenv
    judgeenv.load_env(cli=True)
    from dmoj import executors
    executors.load_executors()
    return sorted(executors.executors)


def run_job(language, source, stdin, time_limit, memory_limit):
    """Executed in a worker process."""
    from dmoj import executors
    from dmoj.error import CompileError
    from dmoj.utils.communicate import safe_communicate, OutputLimitExceeded

    if language not in executors.executors:
        return {'status': 'error', 'message': 'language is not available'}

    started = time.monotonic()
    try:
        executor = executors.executors[language].Executor('main', source.encode('utf-8'))
    except CompileError as e:
        return {'status': 'compile_error', 'compile_output': e.message[:MAX_OUTPUT]}
    except Exception as e:  # compiler crashed, timed out, etc.
        log.exception('compile failed')
        return {'status': 'compile_error', 'compile_output': str(e)[:MAX_OUTPUT]}
    compile_time = time.monotonic() - started
    warning = getattr(executor, 'warning', None) or b''

    proc = executor.launch(time=time_limit, memory=memory_limit, wall_time=time_limit * 3 + 1,
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = safe_communicate(proc, stdin.encode('utf-8'), outlimit=MAX_OUTPUT, errlimit=MAX_OUTPUT)
        ole = False
    except OutputLimitExceeded:
        proc.kill()
        proc.wait()
        stdout, stderr, ole = b'', b'', True

    if proc.is_tle:
        verdict = 'TLE'
    elif proc.is_mle:
        verdict = 'MLE'
    elif ole or proc.is_ole:
        verdict = 'OLE'
    elif proc.returncode != 0:
        verdict = 'RTE'
    else:
        verdict = 'OK'

    result = {
        'status': 'ok',
        'verdict': verdict,
        'stdout': stdout.decode('utf-8', 'replace'),
        'stderr': stderr.decode('utf-8', 'replace'),
        'exit_code': proc.returncode,
        'time': round(proc.execution_time or 0, 3),
        'memory': proc.max_memory,
        'compile_time': round(compile_time, 2),
        'compile_output': warning.decode('utf-8', 'replace')[:MAX_OUTPUT] if isinstance(warning, bytes) else warning,
    }
    if proc.protection_fault:
        syscall, callname, args, update_errno = proc.protection_fault
        result['stderr'] += '\n[заблокирован системный вызов: %s]' % callname
    return result


class Limiter:
    """Per-user limits: one run at a time and at most `per_minute` runs a minute."""

    def __init__(self, per_minute):
        self.per_minute = per_minute
        self.lock = threading.Lock()
        self.history = defaultdict(deque)
        self.active = set()

    def acquire(self, user):
        now = time.monotonic()
        with self.lock:
            if user in self.active:
                return 'Подождите, предыдущий запуск ещё не закончился.'
            hist = self.history[user]
            while hist and now - hist[0] > 60:
                hist.popleft()
            if len(hist) >= self.per_minute:
                return 'Слишком много запусков. Подождите минуту.'
            hist.append(now)
            self.active.add(user)
        return None

    def release(self, user):
        with self.lock:
            self.active.discard(user)


def check_token(secret, token):
    try:
        body, sig = token.split('.', 1)
        expected = base64.urlsafe_b64encode(hmac.new(secret, body.encode(), hashlib.sha256).digest()).decode()
        if not hmac.compare_digest(expected.rstrip('='), sig.rstrip('=')):
            return None
        payload = json.loads(base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)))
    except (ValueError, TypeError):
        return None
    if payload.get('exp', 0) < time.time():
        return None
    return payload


class Handler(BaseHTTPRequestHandler):
    server_version = 'olymp-runner'

    def log_message(self, fmt, *args):
        log.info('%s %s', self.address_string(), fmt % args)

    def cors(self):
        origin = self.headers.get('Origin')
        if origin and origin in self.server.allow_origins:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Vary', 'Origin')

    def reply(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split('?')[0].rstrip('/')
        if path.endswith('/health'):
            self.reply(200, {'ok': True, 'busy': self.server.busy, 'workers': self.server.workers})
        elif path.endswith('/languages'):
            self.reply(200, {'languages': self.server.languages})
        else:
            self.reply(404, {'status': 'error', 'message': 'not found'})

    def do_POST(self):
        if not self.path.split('?')[0].rstrip('/').endswith('/run'):
            return self.reply(404, {'status': 'error', 'message': 'not found'})
        try:
            length = int(self.headers.get('Content-Length', 0))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_SOURCE + MAX_STDIN + 4096:
            return self.reply(413, {'status': 'error', 'message': 'Слишком большой запрос.'})
        try:
            data = json.loads(self.rfile.read(length))
        except ValueError:
            return self.reply(400, {'status': 'error', 'message': 'bad json'})

        payload = check_token(self.server.secret, str(data.get('token', '')))
        if payload is None:
            return self.reply(403, {'status': 'error', 'message': 'Сессия запуска устарела. Обновите страницу.'})

        source = str(data.get('source', ''))
        stdin = str(data.get('stdin', ''))
        language = str(data.get('language', ''))
        if len(source.encode()) > MAX_SOURCE:
            return self.reply(413, {'status': 'error', 'message': 'Код длиннее 64 КБ.'})
        if len(stdin.encode()) > MAX_STDIN:
            return self.reply(413, {'status': 'error', 'message': 'Входные данные больше 1 МБ.'})
        allowed = payload.get('langs')
        if allowed is not None and language not in allowed:
            return self.reply(400, {'status': 'error', 'message': 'Этот язык недоступен.'})

        try:
            time_limit = min(float(payload.get('time') or DEFAULT_TIME), MAX_TIME)
            memory_limit = min(int(payload.get('memory') or DEFAULT_MEMORY), MAX_MEMORY)
        except (TypeError, ValueError):
            time_limit, memory_limit = DEFAULT_TIME, DEFAULT_MEMORY

        user = payload.get('u')
        error = self.server.limiter.acquire(user)
        if error:
            return self.reply(429, {'status': 'error', 'message': error})
        try:
            with self.server.busy_lock:
                if self.server.busy >= self.server.workers + self.server.queue:
                    return self.reply(503, {'status': 'error', 'message': 'Сервер занят, попробуйте через минуту.'})
                self.server.busy += 1
            try:
                future = self.server.pool.submit(run_job, language, source, stdin, time_limit, memory_limit)
                result = future.result(timeout=90)
            except FutureTimeout:
                result = {'status': 'error', 'message': 'Запуск занял слишком много времени.'}
            except BrokenProcessPool:
                log.error('worker pool died, restarting it')
                self.server.restart_pool()
                result = {'status': 'error', 'message': 'Внутренняя ошибка запуска, попробуйте ещё раз.'}
            except Exception:
                log.exception('run failed')
                result = {'status': 'error', 'message': 'Внутренняя ошибка запуска.'}
            finally:
                with self.server.busy_lock:
                    self.server.busy -= 1
        finally:
            self.server.limiter.release(user)
        self.reply(200, result)


def main():
    parser = argparse.ArgumentParser(description='Code runner for the olymp editor')
    parser.add_argument('--config', required=True, help='judge.yml with the runtime section')
    parser.add_argument('--listen', default='127.0.0.1:9910')
    parser.add_argument('--secret-file', required=True, help='file with the secret shared with the site')
    parser.add_argument('--workers', type=int, default=2, help='programs run at the same time')
    parser.add_argument('--queue', type=int, default=8, help='requests allowed to wait for a worker')
    parser.add_argument('--per-minute', type=int, default=20, help='runs per user per minute')
    parser.add_argument('--only-executors', default='', help='comma separated executor ids')
    parser.add_argument('--allow-origin', action='append', default=[], help='origin allowed for CORS (dev)')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    with open(args.secret_file, 'rb') as f:
        secret = f.read().strip()
    if len(secret) < 16:
        raise SystemExit('secret is too short')

    languages = load_judge(args.config, args.only_executors)
    log.info('languages: %s', ', '.join(languages))

    host, port = args.listen.rsplit(':', 1)
    server = ThreadingHTTPServer((host, int(port)), Handler)
    server.daemon_threads = True
    server.secret = secret
    server.languages = languages
    server.limiter = Limiter(args.per_minute)
    server.workers = args.workers
    server.queue = args.queue
    server.busy = 0
    server.busy_lock = threading.Lock()
    server.allow_origins = set(args.allow_origin)

    def restart_pool():
        old = getattr(server, 'pool', None)
        server.pool = ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('fork'))
        if old is not None:
            old.shutdown(wait=False, cancel_futures=True)

    server.restart_pool = restart_pool
    restart_pool()
    log.info('listening on %s', args.listen)
    try:
        server.serve_forever()
    finally:
        server.pool.shutdown(cancel_futures=True)


if __name__ == '__main__':
    os.umask(0o022)
    main()
