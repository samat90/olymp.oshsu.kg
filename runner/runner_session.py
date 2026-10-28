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
from runner_clean import clean
from runner_exec import RunnerError, build_executor, verdict_of

log = logging.getLogger('runner')

MAX_SESSION_OUTPUT = 1 << 20
CLOCK_TICKS = os.sysconf('SC_CLK_TCK')


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
            ws.send_json(sock, {'type': 'compile_error', 'output': clean(e.message)})
            return
        if compiled is not None:
            compiled.set()
        warning = getattr(executor, 'warning', None) or b''
        if isinstance(warning, bytes):
            warning = warning.decode('utf-8', 'replace')
        ws.send_json(sock, {'type': 'started', 'compile_time': round(time.monotonic() - started, 2),
                            'warning': clean(warning)[:65536]})

        deadline = time.monotonic() + wall_limit
        # The judge's own time limit counts the time a program waits in read() as well, so a program
        # waiting for the user's input would be stopped after a few seconds. Here it is only the overall
        # cap (a backstop: it runs late), and both limits are checked by this loop instead.
        proc = executor.launch(*args, time=wall_limit + 60, memory=memory_limit, wall_time=wall_limit + 60,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        streams = {proc.stdout.fileno(): ('out', codecs.getincrementaldecoder('utf-8')('replace')),
                   proc.stderr.fileno(): ('err', codecs.getincrementaldecoder('utf-8')('replace'))}
        total = 0
        ole = False
        cpu_tle = wall_tle = False
        used = 0
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
                        ws.send_json(sock, {'type': kind, 'data': clean(tail) if kind == 'err' else tail})
                    continue
                total += len(data)
                if total > MAX_SESSION_OUTPUT:
                    ole = True
                    proc.kill()
                    continue
                text = decoder.decode(data)
                if text:
                    ws.send_json(sock, {'type': kind, 'data': clean(text) if kind == 'err' else text})
            if not client_open:
                proc.kill()
            used = max(used, cpu_seconds(proc))
            if not cpu_tle and used > cpu_limit:
                cpu_tle = True
                proc.kill()
            if not wall_tle and time.monotonic() > deadline:
                wall_tle = True
                proc.kill()

        proc.wait()
        used = max(used, proc.cpu_time or 0)
        ws.send_json(sock, {
            'type': 'exit',
            'verdict': 'TLE' if cpu_tle or wall_tle else verdict_of(proc, ole),
            'exit_code': proc.returncode,
            'time': round(used, 3),
            'memory': proc.max_memory,
            # Stopped by the overall cap: the program was waiting (for input, or in sleep), not computing.
            'wall': (wall_tle or proc.is_tle) and not cpu_tle,
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


def cpu_seconds(proc):
    """User + system CPU time of the running program, from /proc (0 once it is gone)."""
    try:
        with open('/proc/%d/stat' % proc.pid) as f:
            fields = f.read().rpartition(')')[2].split()
        # utime, stime, cutime, cstime are fields 14-17 of stat, 12-15 after the name.
        return sum(int(x) for x in fields[11:15]) / CLOCK_TICKS
    except (OSError, ValueError, IndexError, TypeError):
        return 0


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
