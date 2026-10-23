"""Verify CPython 3.14.7 in the real DMOJ sandbox before switching PY3."""
import subprocess

from dmoj.error import CompileError
from dmoj.executors.PY3 import Executor
from dmoj.cptbox.filesystem_policies import RecursiveDir

Executor.runtime_dict = {'python3': '/opt/python/3.14.7/bin/python3.14'}
# Mirrors the scoped read-only extra_fs rule installed in judge.yml.
Executor.fs = [*Executor.fs, RecursiveDir('/opt/python/3.14.7')]


def run(name, code, data=b'', time=2, memory=65536):
    executor = Executor(name, code.encode())
    process = executor.launch(time=time, wall_time=5, memory=memory,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate(data)
    print(name, 'exit=', process.returncode, 'TLE=', process.is_tle, 'MLE=', process.is_mle,
          'sandbox=', bool(process.protection_fault), flush=True)
    return process, out, err


assert Executor.run_self_test()
for name, code, data, expected in [
    ('version', 'import sys; print(".".join(map(str, sys.version_info[:3])))', b'', b'3.14.7'),
    ('sum', 'import sys; a=list(map(int,sys.stdin.buffer.read().split())); print(sum(a[1:]))', b'4\n1000000000 -2 3 4\n', b'1000000005'),
    ('templates', 'x = 42; value = t"Answer: {x}"; print(value.interpolations[0].value)', b'', b'42'),
    ('libraries', 'import heapq, collections, bisect, itertools, functools, math, decimal, fractions, json; print(math.isqrt(10**18))', b'', b'1000000000'),
    ('zstd', 'from compression import zstd; print(zstd.decompress(zstd.compress(b"hello")).decode())', b'', b'hello'),
    ('unicode', 'print("Кыргызча / Русский")', b'', 'Кыргызча / Русский'.encode()),
]:
    process, out, err = run(name, code, data)
    assert process.returncode == 0 and out.strip() == expected and not err, (name, out, err)

try:
    Executor('invalid', b'print(')
except CompileError:
    print('compile_error: PASS')
else:
    raise AssertionError('Invalid Python compiled')
process, _, err = run('runtime_error', 'raise ValueError("test")')
assert process.returncode != 0 and b'ValueError' in err
process, _, _ = run('time_limit', 'while True: pass', time=0.2)
assert process.is_tle
process, _, err = run('memory_limit', 'a=[]\nwhile True: a.append(b"x" * (4 * 1024 * 1024))')
assert process.is_mle or (process.returncode != 0 and b'MemoryError' in err)
for name, code in [
    ('read_private', 'open("/home/admin/judge-config/judge.yml").read()'),
    ('write_outside', 'open("/tmp/olymp-python-forbidden", "w").write("test")'),
    ('network', 'import socket; socket.socket()'),
    ('spawn', 'import subprocess; subprocess.run(["/usr/bin/true"])'),
]:
    process, out, err = run(name, code + '\nprint("ESCAPED")')
    assert b'ESCAPED' not in out and process.returncode != 0, name
print('PASS: Python 3.14.7, modern syntax, standard library, limits and sandbox isolation.')
