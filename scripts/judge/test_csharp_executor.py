"""Run with the judge-server virtualenv on Linux before enabling CSHARP."""
import subprocess

from dmoj.error import CompileError
from dmoj.executors.CSHARP import Executor


Executor.runtime_dict = {'dotnet': '/usr/bin/dotnet'}


def run(name, source, data=b'', time=2, memory=65536, cached=False):
    executor = Executor(name, source.encode(), cached=cached)
    process = executor.launch(time=time, wall_time=5, memory=memory,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate(data)
    print(name, 'exit=', process.returncode, 'time=', round(process.execution_time, 3),
          'memory=', process.max_memory, 'TLE=', process.is_tle, 'MLE=', process.is_mle,
          'sandbox=', bool(process.protection_fault), flush=True)
    return process, out, err


assert Executor.run_self_test()
for name, source, data, answer in [
    ('top_level', 'using System; using System.Linq; Console.WriteLine(Console.ReadLine().Split().Select(long.Parse).Sum());', b'20 22\n', b'42'),
    ('classic', 'using System; class Program { static void Main() { Console.WriteLine(42); } }', b'', b'42'),
    ('modern', 'using System; record Point(int X, int Y); class Program { static void Main() { int[] a = [1, 2, 3]; Console.WriteLine(new Point(a[0], a[^1])); } }', b'', b'Point { X = 1, Y = 3 }'),
    ('libraries', 'using System; using System.Numerics; Console.WriteLine(BigInteger.Pow(2, 100));', b'', b'1267650600228229401496703205376'),
    ('unicode', 'using System; Console.WriteLine("Кыргызча / Русский");', b'', 'Кыргызча / Русский'.encode()),
]:
    process, out, err = run(name, source, data)
    assert process.returncode == 0 and out.strip() == answer and not err, (name, out, err)

for _ in range(2):
    process, out, err = run('cached', 'System.Console.WriteLine(42);', cached=True)
    assert process.returncode == 0 and out.strip() == b'42' and not err

process, _, err = run('runtime_error', 'throw new System.InvalidOperationException("test exception");')
assert process.returncode != 0 and b'InvalidOperationException' in err

try:
    Executor('bad_syntax', b'using System; Console.WriteLine(;')
except CompileError as error:
    assert b'error CS' in bytes(str(error), 'utf-8')
    print('compile_error: PASS')
else:
    raise AssertionError('Invalid C# compiled')

process, _, _ = run('time_limit', 'while (true) {}', time=0.2)
assert process.is_tle
process, _, _ = run('wall_limit', 'System.Threading.Thread.Sleep(60000);', time=0.2)
assert process.is_tle
process, _, err = run('memory_limit', 'using System.Collections.Generic; var list = new List<byte[]>(); while(true) { var b = new byte[4194304]; System.Array.Fill(b, (byte)1); list.Add(b); }')
assert process.is_mle, err

for name, code in [
    ('read_private', 'System.IO.File.ReadAllText("/home/admin/judge-config/judge.yml")'),
    ('write_outside', 'System.IO.File.WriteAllText("/tmp/olymp-sandbox-must-not-exist", "bad")'),
]:
    process, out, _ = run(name, 'try { ' + code + '; System.Console.WriteLine("ESCAPED"); } catch { System.Console.WriteLine("BLOCKED"); }')
    assert b'ESCAPED' not in out and (b'BLOCKED' in out or process.protection_fault)

process, out, err = run('network', 'using System.Net.Sockets; try { var socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp); System.Console.WriteLine("ESCAPED"); } catch (SocketException) { System.Console.WriteLine("BLOCKED"); }')
assert b'BLOCKED' in out or process.protection_fault, (out, err)
process, out, _ = run('spawn', 'System.Diagnostics.Process.Start("/usr/bin/true").WaitForExit(); System.Console.WriteLine("ESCAPED");')
assert b'ESCAPED' not in out and process.returncode != 0

print('All C# compiler, runtime, resource-limit and isolation checks passed.')
