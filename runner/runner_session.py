"""Interactive run: the program works while the user types into the terminal.

Runs in its own forked process, one per session. Messages (JSON over WebSocket):

    client -> server  {"type": "in", "data": "5\\n"} | {"type": "eof"} | {"type": "kill"}
    server -> client  {"type": "status", "text": ...}
                      {"type": "compile_error", "output": ...}
                      {"type": "started", "compile_time": ..., "warning": ...}
                      {"type": "out" | "err", "data": ...}
                      {"type": "exit", "verdict": ..., "exit_code": ..., "time": ..., "memory": ...}
"""
import codecs
import json
import logging
import os
import select
import subprocess
import time

import runner_ws as ws
from runner_exec import RunnerError, build_executor, verdict_of

log = logging.getLogger('runner')

MAX_SESSION_OUTPUT = 1 << 20


def run_session(sock, language, source, extra, args, cpu_limit, memory_limit, wall_limit, compiled=None):
    from dmoj.error import CompileError

    try:
        ws.send_json(sock, {'type': 'status', 'text': 'compiling'})
        started = time.monotonic()
        try:
            executor = build_executor(language, source, extra, unbuffered=True, cached=False)
        except RunnerError as e:
            ws.send_json(sock, {'type': 'compile_error', 'output': str(e)})
            return
        except CompileError as e:
            ws.send_json(sock, {'type': 'compile_error', 'output': e.message})
            return
        if compiled is not None:
            compiled.set()
        warning = getattr(executor, 'warning', None) or b''
        if isinstance(warning, bytes):
            warning = warning.decode('utf-8', 'replace')
        ws.send_json(sock, {'type': 'started', 'compile_time': round(time.monotonic() - started, 2),
                            'warning': warning[:65536]})

        proc = executor.launch(*args, time=cpu_limit, memory=memory_limit, wall_time=wall_limit,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        streams = {proc.stdout.fileno(): ('out', codecs.getincrementaldecoder('utf-8')('replace')),
                   proc.stderr.fileno(): ('err', codecs.getincrementaldecoder('utf-8')('replace'))}
        total = 0
        ole = False
        client_open = True

        while streams:
            watch = list(streams) + ([sock] if client_open else [])
            readable, _, _ = select.select(watch, [], [], 0.5)
            for fd in readable:
                if fd is sock:
                    client_open = handle_client(sock, proc)
                    continue
                data = os.read(fd, 8192)
                kind, decoder = streams[fd]
                if not data:
                    del streams[fd]
                    tail = decoder.decode(b'', final=True)
                    if tail:
                        ws.send_json(sock, {'type': kind, 'data': tail})
                    continue
                total += len(data)
                if total > MAX_SESSION_OUTPUT:
                    ole = True
                    proc.kill()
                    continue
                text = decoder.decode(data)
                if text:
                    ws.send_json(sock, {'type': kind, 'data': text})
            if not client_open:
                proc.kill()

        proc.wait()
        ws.send_json(sock, {
            'type': 'exit',
            'verdict': verdict_of(proc, ole),
            'exit_code': proc.returncode,
            'time': round(proc.execution_time or 0, 3),
            'memory': proc.max_memory,
            'wall': proc.is_tle and (proc.execution_time or 0) < cpu_limit,
        })
    except (ws.Closed, OSError):
        pass
    except Exception:
        log.exception('session failed')
        try:
            ws.send_json(sock, {'type': 'compile_error', 'output': 'Внутренняя ошибка запуска.'})
        except OSError:
            pass
    finally:
        if compiled is not None:
            compiled.set()
        ws.close(sock)


def handle_client(sock, proc):
    """Reads one message from the browser. Returns False when the client is gone."""
    opcode, payload = ws.recv_frame(sock)
    if opcode == 0x8:
        return False
    if opcode == 0x9:
        ws.send_frame(sock, payload, opcode=0xA)
        return True
    if opcode != 0x1:
        return True
    try:
        message = json.loads(payload)
    except ValueError:
        return True
    kind = message.get('type')
    try:
        if kind == 'in' and proc.stdin is not None and not proc.stdin.closed:
            proc.stdin.write(str(message.get('data', '')).encode('utf-8'))
            proc.stdin.flush()
        elif kind == 'eof' and proc.stdin is not None and not proc.stdin.closed:
            proc.stdin.close()
        elif kind == 'kill':
            proc.kill()
    except (BrokenPipeError, OSError):
        pass
    return True
