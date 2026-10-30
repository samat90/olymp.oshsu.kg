#!/usr/bin/env python3
"""Code runner for the online editor and the Compiler section.

Runs next to the judge and uses the judge's own executors, so the editor
supports exactly the languages (and compilers, and sandbox) used for grading.

The site signs a short-lived token for the logged-in user; the browser sends
it with the code. The runner never talks to the database.

    python runner/server.py --config /home/judge/judge-config/judge.yml \
        --listen 127.0.0.1:9910 --secret-file /home/judge/runner.secret

Endpoints:
    POST /run       run with prepared input (several inputs = compile once, run each)
    GET  /session   WebSocket: interactive run in a terminal
    POST /poll/start, GET /poll/<id>?since=N, POST /poll/<id>/send
                    the same interactive run over plain HTTP, for networks without WebSocket
    POST /format    format code with clang-format
    GET  /health, /languages
"""
import argparse
import base64
import hashlib
import hmac
import json
import logging
import multiprocessing
import os
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
from collections import defaultdict, deque
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FutureTimeout
from concurrent.futures.process import BrokenProcessPool
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# The judge package is also called "dmoj", so only this folder goes on the path, not the site.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import runner_ws as ws  # noqa: E402
from runner_exec import RunnerError, clean_files, run_job  # noqa: E402

log = logging.getLogger('runner')

MAX_SOURCE = 65536
MAX_STDIN = 1 << 20
MAX_BATCH = 10          # inputs per request ("test on samples" compiles once)
MAX_ARGS = 20
MAX_TIME = 5.0          # CPU seconds for the program itself
MAX_MEMORY = 262144     # KB
DEFAULT_TIME = 2.0
DEFAULT_MEMORY = 262144
SESSION_CPU = 10.0      # CPU seconds of an interactive run (time spent waiting for input is free)
SESSION_WALL = 900      # overall cap of an interactive run: it may wait for input this long
CLANG_FORMAT_LANGS = {
    'C': 'c', 'C11': 'c', 'CPP03': 'cpp', 'CPP11': 'cpp', 'CPP14': 'cpp', 'CPP17': 'cpp', 'CPP20': 'cpp',
    'CPP23': 'cpp', 'JAVA': 'java', 'JAVA8': 'java', 'NODEJS': 'js', 'MONOCS': 'cs', 'CSHARP': 'cs',
}


def code_version():
    """Short hash of the runner's code, so a deploy can check which code is running (scripts/server/sync_runner.sh)."""
    folder = os.path.dirname(os.path.abspath(__file__))
    names = sorted(n for n in os.listdir(folder) if n == 'server.py' or n.startswith('runner_') and n.endswith('.py'))
    digest = hashlib.sha256()
    for name in names:
        with open(os.path.join(folder, name), 'rb') as f:
            digest.update(f.read())
    return digest.hexdigest()[:12]


VERSION = code_version()


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


class WorkerSet:
    """Single-process pools. The same code goes to the same worker, so pressing Run again
    with other input reuses the compiled program from that worker's cache."""

    def __init__(self, count):
        self.lock = threading.Lock()
        self.pools = [self._new_pool() for _ in range(count)]
        self.busy = [0] * count

    @staticmethod
    def _new_pool():
        return ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context('fork'))

    def run(self, key, fn, *args):
        with self.lock:
            preferred = int(hashlib.md5(key.encode('utf-8', 'replace')).hexdigest(), 16) % len(self.pools)
            least = min(range(len(self.pools)), key=lambda i: self.busy[i])
            # Keep the cache-friendly worker unless it is clearly busier than another one.
            index = preferred if self.busy[preferred] <= self.busy[least] + 1 else least
            self.busy[index] += 1
            pool = self.pools[index]
        try:
            return pool.submit(fn, *args).result(timeout=90)
        except BrokenProcessPool:
            log.error('worker %d died, starting a new one', index)
            with self.lock:
                if self.pools[index] is pool:
                    self.pools[index] = self._new_pool()
            pool.shutdown(wait=False, cancel_futures=True)
            raise
        finally:
            with self.lock:
                self.busy[index] -= 1

    def shutdown(self):
        for pool in self.pools:
            pool.shutdown(cancel_futures=True)


class Limiter:
    """Per-user limits: one run at a time and at most `per_minute` runs a minute."""

    def __init__(self, per_minute):
        self.per_minute = per_minute
        self.lock = threading.Lock()
        self.history = defaultdict(deque)
        self.active = defaultdict(int)

    def acquire(self, user, parallel=1):
        now = time.monotonic()
        with self.lock:
            if self.active[user] >= parallel:
                return 'Подождите, предыдущий запуск ещё не закончился.'
            hist = self.history[user]
            while hist and now - hist[0] > 60:
                hist.popleft()
            if len(hist) >= self.per_minute:
                return 'Слишком много запусков. Подождите минуту.'
            hist.append(now)
            self.active[user] += 1
        return None

    def release(self, user):
        with self.lock:
            self.active[user] -= 1
            if self.active[user] <= 0:
                del self.active[user]


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


def parse_program(data, payload):
    """Common checks for /run and /session. Returns (language, source, extra, args) or raises RunnerError."""
    language = str(data.get('language', ''))
    allowed = payload.get('langs')
    if allowed is not None and language not in allowed:
        raise RunnerError('Этот язык недоступен.')
    source = str(data.get('source', ''))
    if len(source.encode()) > MAX_SOURCE:
        raise RunnerError('Код длиннее 64 КБ.')
    extra = clean_files(data.get('files'), str(data.get('main', '')))
    args = data.get('args') or []
    if not isinstance(args, list):
        args = []
    args = [str(a)[:200] for a in args[:MAX_ARGS]]
    return language, source, extra, args


def session_child(sock, language, source, extra, args, memory_limit, compiled):
    from runner_session import run_session
    try:
        run_session(sock, language, source, extra, args, SESSION_CPU, memory_limit, SESSION_WALL, compiled)
    finally:
        # The child is forked from a process with many threads; a lock one of them held at that moment
        # (the log stream, for example) stays locked here forever, and the normal interpreter exit
        # would wait for it. Leave without the usual clean-up.
        os._exit(0)


def serve_session(server, sock):
    """Runs one interactive session over `sock`, which speaks WebSocket frames: the browser's own
    connection, or one end of a socket pair when the browser polls over plain HTTP (PollSession)."""
    try:
        opcode, raw = ws.recv_frame(sock)
        data = json.loads(raw) if opcode == 0x1 else {}
    except (ws.Closed, OSError, ValueError):
        return
    payload = check_token(server.secret, str(data.get('token', '')))
    if payload is None:
        ws.send_json(sock, {'type': 'compile_error', 'output': 'Сессия запуска устарела. Обновите страницу.'})
        return ws.close(sock)
    try:
        language, source, extra, args = parse_program(data, payload)
    except RunnerError as e:
        ws.send_json(sock, {'type': 'compile_error', 'output': str(e)})
        return ws.close(sock)

    user = payload.get('u')
    error = server.limiter.acquire(user)
    if error:
        ws.send_json(sock, {'type': 'compile_error', 'output': error})
        return ws.close(sock)
    try:
        with server.busy_lock:
            if server.sessions >= server.max_sessions:
                ws.send_json(sock, {'type': 'compile_error', 'output': 'Сервер занят, попробуйте через минуту.'})
                return ws.close(sock)
            server.sessions += 1
        try:
            memory_limit = min(int(payload.get('memory') or DEFAULT_MEMORY), MAX_MEMORY)
            sock.settimeout(None)
            # Compiling takes a whole core, so at most `workers` terminals compile at the same time;
            # the others wait their turn. Waiting for the user's input costs almost nothing.
            if not server.compile_gate.acquire(timeout=0):
                ws.send_json(sock, {'type': 'status', 'text': 'queued'})
                if not server.compile_gate.acquire(timeout=120):
                    busy = 'Сервер занят, попробуйте через минуту.'
                    ws.send_json(sock, {'type': 'compile_error', 'output': busy})
                    return ws.close(sock)
            ctx = multiprocessing.get_context('fork')
            compiled = ctx.Event()
            try:
                child = ctx.Process(target=session_child,
                                    args=(sock, language, source, extra, args, memory_limit, compiled))
                child.start()
                deadline = time.monotonic() + 60
                while not compiled.wait(0.5) and child.is_alive() and time.monotonic() < deadline:
                    pass
            finally:
                server.compile_gate.release()
            child.join(SESSION_WALL + 120)
            if child.is_alive():
                child.kill()
        finally:
            with server.busy_lock:
                server.sessions -= 1
    finally:
        server.limiter.release(user)


class PollSession:
    """An interactive session for browsers whose network does not pass WebSocket (a proxy in the way).

    The session runs exactly as over WebSocket (serve_session), but on one end of a socket pair;
    this object holds the other end. Messages from the program are kept in a list that the browser
    reads with GET /poll/<id>?since=N (long polling), and its input comes with POST /poll/<id>/send.
    """
    POLL_WAIT = 15      # seconds a poll request waits for new messages
    IDLE_LIMIT = 45     # a session nobody polls for this long is killed
    KEEP_DONE = 60      # a finished session is kept this long for the last poll

    def __init__(self, server, start):
        self.id = secrets.token_urlsafe(24)
        self.messages = []
        self.done = False
        self.finished = 0
        self.seen = time.monotonic()
        self.cond = threading.Condition()
        self.send_lock = threading.Lock()
        self.sock, inner = socket.socketpair()
        ws.send_json(self.sock, start)
        threading.Thread(target=self._serve, args=(server, inner), daemon=True).start()
        threading.Thread(target=self._pump, daemon=True).start()

    @staticmethod
    def _serve(server, inner):
        try:
            serve_session(server, inner)
        finally:
            inner.close()

    def _pump(self):
        try:
            while True:
                opcode, payload = ws.recv_frame(self.sock)
                if opcode == 0x8:
                    break
                if opcode == 0x1:
                    message = json.loads(payload)
                    with self.cond:
                        self.messages.append(message)
                        self.cond.notify_all()
        except (ws.Closed, OSError, ValueError):
            pass
        with self.cond:
            self.done = True
            self.finished = time.monotonic()
            self.cond.notify_all()
        try:
            self.sock.close()
        except OSError:
            pass

    def send(self, message):
        try:
            with self.send_lock:
                ws.send_json(self.sock, message)
        except OSError:
            pass

    def poll(self, since):
        """Returns (messages after `since`, True when the session has ended and nothing is left)."""
        deadline = time.monotonic() + self.POLL_WAIT
        with self.cond:
            self.seen = time.monotonic()
            while len(self.messages) <= since and not self.done:
                left = deadline - time.monotonic()
                if left <= 0:
                    break
                self.cond.wait(left)
            self.seen = time.monotonic()
            return self.messages[since:], self.done

    def expired(self, now):
        if self.done:
            return now - self.finished > self.KEEP_DONE
        if now - self.seen > self.IDLE_LIMIT:
            # The browser is gone: stop the program, the pump then marks the session done.
            self.send({'type': 'kill'})
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        return False


def reap_poll_sessions(server):
    while True:
        time.sleep(10)
        now = time.monotonic()
        with server.poll_lock:
            for key in [k for k, v in server.poll_sessions.items() if v.expired(now)]:
                del server.poll_sessions[key]


class BoundedServer(ThreadingHTTPServer):
    """A thread per connection, but never more than `max_connections` of them: a flood of idle
    connections cannot use up the machine's memory or threads."""

    daemon_threads = True
    request_queue_size = 128

    def __init__(self, address, handler, max_connections):
        super().__init__(address, handler)
        self.slots = threading.BoundedSemaphore(max_connections)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            log.warning('too many connections, dropping %s', client_address[0])
            self.shutdown_request(request)
            return
        super().process_request(request, client_address)

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()


class Handler(BaseHTTPRequestHandler):
    server_version = 'olymp-runner'
    timeout = 30  # a client that does not send its request in time is dropped

    def log_message(self, fmt, *args):
        if '/poll/' in self.path and ' 200 ' in ' %s ' % (fmt % args):
            return  # a running terminal polls several times a second
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

    def route(self):
        return self.path.split('?')[0].rstrip('/').rsplit('/', 1)[-1]

    def poll_route(self):
        """('start', None) | ('poll', id) | ('send', id) for /poll/... paths, else (None, None)."""
        parts = self.path.split('?')[0].strip('/').split('/')
        if len(parts) >= 2 and parts[-2] == 'poll':
            return ('start', None) if parts[-1] == 'start' else ('poll', parts[-1])
        if len(parts) >= 3 and parts[-3] == 'poll' and parts[-1] == 'send':
            return 'send', parts[-2]
        return None, None

    def poll_session(self, key):
        with self.server.poll_lock:
            return self.server.poll_sessions.get(key)

    def do_GET(self):
        route = self.route()
        if route == 'health':
            self.reply(200, {'ok': True, 'busy': self.server.busy, 'workers': self.server.workers,
                             'sessions': self.server.sessions, 'version': VERSION})
        elif route == 'languages':
            self.reply(200, {'languages': self.server.languages})
        elif route == 'session' and self.headers.get('Upgrade', '').lower() == 'websocket':
            self.handle_session()
        elif self.poll_route()[0] == 'poll':
            self.handle_poll(self.poll_route()[1])
        else:
            self.reply(404, {'status': 'error', 'message': 'not found'})

    def read_json(self, limit):
        try:
            length = int(self.headers.get('Content-Length', 0))
        except ValueError:
            length = 0
        if length <= 0 or length > limit:
            self.reply(413, {'status': 'error', 'message': 'Слишком большой запрос.'})
            return None
        try:
            return json.loads(self.rfile.read(length))
        except ValueError:
            self.reply(400, {'status': 'error', 'message': 'bad json'})
            return None

    def do_POST(self):
        route = self.route()
        if route == 'run':
            self.handle_run()
        elif route == 'format':
            self.handle_format()
        elif self.poll_route()[0] == 'start':
            self.handle_poll_start()
        elif self.poll_route()[0] == 'send':
            self.handle_poll_send(self.poll_route()[1])
        else:
            self.reply(404, {'status': 'error', 'message': 'not found'})

    # ---- /run ----

    def handle_run(self):
        data = self.read_json(MAX_SOURCE + MAX_STDIN + 300 * 1024)
        if data is None:
            return
        payload = check_token(self.server.secret, str(data.get('token', '')))
        if payload is None:
            return self.reply(403, {'status': 'error', 'message': 'Сессия запуска устарела. Обновите страницу.'})
        try:
            language, source, extra, args = parse_program(data, payload)
        except RunnerError as e:
            return self.reply(400, {'status': 'error', 'message': str(e)})

        stdins = data.get('stdins')
        if not isinstance(stdins, list) or not stdins:
            stdins = [data.get('stdin', '')]
        stdins = [str(x) for x in stdins[:MAX_BATCH]]
        if len(''.join(stdins).encode()) > MAX_STDIN:
            return self.reply(413, {'status': 'error', 'message': 'Входные данные больше 1 МБ.'})

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
                key = language + '\0' + source + '\0' + json.dumps(sorted(extra))
                result = self.server.workers_set.run(key, run_job, language, source, extra, stdins, args,
                                                     time_limit, memory_limit)
            except FutureTimeout:
                result = {'status': 'error', 'message': 'Запуск занял слишком много времени.'}
            except BrokenProcessPool:
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

    # ---- /session (WebSocket) ----

    def handle_session(self):
        key = self.headers.get('Sec-WebSocket-Key')
        origin = self.headers.get('Origin')
        bad_origin = bool(self.server.allow_origins and origin and origin not in self.server.allow_origins)
        if not key or bad_origin:
            return self.reply(403, {'status': 'error', 'message': 'forbidden'})
        self.send_response(101, 'Switching Protocols')
        self.send_header('Upgrade', 'websocket')
        self.send_header('Connection', 'Upgrade')
        self.send_header('Sec-WebSocket-Accept', ws.accept_key(key))
        self.end_headers()
        self.wfile.flush()
        sock = self.connection
        sock.settimeout(30)
        self.close_connection = True

        serve_session(self.server, sock)

    # ---- /poll (the interactive session over plain HTTP) ----

    def handle_poll_start(self):
        data = self.read_json(MAX_SOURCE + 300 * 1024)
        if data is None:
            return
        # The token is checked here too, so strangers cannot fill the session table.
        if check_token(self.server.secret, str(data.get('token', ''))) is None:
            return self.reply(403, {'status': 'error', 'message': 'Сессия запуска устарела. Обновите страницу.'})
        with self.server.poll_lock:
            if len(self.server.poll_sessions) >= self.server.max_sessions * 2:
                return self.reply(503, {'status': 'error', 'message': 'Сервер занят, попробуйте через минуту.'})
            session = PollSession(self.server, data)
            self.server.poll_sessions[session.id] = session
        self.reply(200, {'status': 'ok', 'id': session.id})

    def handle_poll(self, key):
        session = self.poll_session(key)
        if session is None:
            return self.reply(404, {'status': 'error', 'message': 'not found'})
        try:
            since = max(0, int(self.path.partition('since=')[2].split('&')[0] or 0))
        except ValueError:
            since = 0
        messages, done = session.poll(since)
        self.reply(200, {'messages': messages, 'next': since + len(messages), 'done': done})

    def handle_poll_send(self, key):
        data = self.read_json(70000)
        if data is None:
            return
        session = self.poll_session(key)
        if session is None:
            return self.reply(404, {'status': 'error', 'message': 'not found'})
        if data.get('type') in ('in', 'eof', 'kill'):
            session.send({'type': data['type'], 'data': str(data.get('data', ''))[:65536]})
        self.reply(200, {'status': 'ok'})

    # ---- /format ----

    def handle_format(self):
        data = self.read_json(MAX_SOURCE + 4096)
        if data is None:
            return
        if check_token(self.server.secret, str(data.get('token', ''))) is None:
            return self.reply(403, {'status': 'error', 'message': 'Сессия устарела. Обновите страницу.'})
        lang = CLANG_FORMAT_LANGS.get(str(data.get('language', '')))
        tool = shutil.which('clang-format')
        if lang is None or tool is None:
            return self.reply(200, {'status': 'unsupported'})
        source = str(data.get('source', ''))[:MAX_SOURCE]
        style = '{BasedOnStyle: Google, IndentWidth: %d, ColumnLimit: 110}' % (
            4 if int(data.get('indent') or 4) == 4 else 2)
        try:
            out = subprocess.run([tool, '--assume-filename=main.' + lang, '--style=' + style],
                                 input=source.encode(), capture_output=True, timeout=5)
        except subprocess.TimeoutExpired:
            return self.reply(200, {'status': 'error', 'message': 'Форматирование заняло слишком много времени.'})
        if out.returncode != 0:
            return self.reply(200, {'status': 'error', 'message': out.stderr.decode('utf-8', 'replace')[:2000]})
        self.reply(200, {'status': 'ok', 'source': out.stdout.decode('utf-8', 'replace')})


def main():
    parser = argparse.ArgumentParser(description='Code runner for the olymp editor')
    parser.add_argument('--config', required=True, help='judge.yml with the runtime section')
    parser.add_argument('--listen', default='127.0.0.1:9910')
    parser.add_argument('--secret-file', required=True, help='file with the secret shared with the site')
    parser.add_argument('--workers', type=int, default=0,
                        help='programs run at the same time (default: one per CPU core)')
    parser.add_argument('--queue', type=int, default=0,
                        help='requests allowed to wait for a worker (default: 4 per worker)')
    parser.add_argument('--max-sessions', type=int, default=64, help='interactive terminals at the same time')
    parser.add_argument('--per-minute', type=int, default=20, help='runs per user per minute')
    parser.add_argument('--only-executors', default='', help='comma separated executor ids')
    parser.add_argument('--allow-origin', action='append', default=[], help='origin allowed for CORS (dev)')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    # The runner is started with a lower CPU priority than the judges (see olymp-runner.service),
    # so it may use every core: grading still gets the CPU first.
    args.workers = args.workers or os.cpu_count() or 2
    args.queue = args.queue or args.workers * 4
    with open(args.secret_file, 'rb') as f:
        secret = f.read().strip()
    if len(secret) < 16:
        raise SystemExit('secret is too short')

    languages = load_judge(args.config, args.only_executors)
    log.info('languages: %s', ', '.join(languages))

    host, port = args.listen.rsplit(':', 1)
    server = BoundedServer((host, int(port)), Handler, args.max_sessions + args.queue + args.workers + 64)
    server.secret = secret
    server.languages = languages
    server.limiter = Limiter(args.per_minute)
    server.workers = args.workers
    server.queue = args.queue
    server.max_sessions = args.max_sessions
    server.busy = 0
    server.sessions = 0
    server.busy_lock = threading.Lock()
    server.compile_gate = threading.BoundedSemaphore(args.workers)
    server.allow_origins = set(args.allow_origin)
    server.workers_set = WorkerSet(args.workers)
    server.poll_sessions = {}
    server.poll_lock = threading.Lock()
    threading.Thread(target=reap_poll_sessions, args=(server,), daemon=True).start()
    log.info('listening on %s, %d workers, queue %d, %d terminals', args.listen, args.workers, args.queue,
             args.max_sessions)
    try:
        server.serve_forever()
    finally:
        server.workers_set.shutdown()


if __name__ == '__main__':
    os.umask(0o022)
    main()
