"""Microsoft F# on .NET 10 for DMOJ (install in dmoj/executors next to CSHARP.py).

Same sandbox and runtime settings as the C# executor; only the compiler differs:
the F# compiler that ships with the .NET SDK (sdk/10.*/FSharp/fsc.dll).
"""
import glob
import os
import shutil

from dmoj.cptbox.handlers import ACCESS_ENOSYS
from dmoj.executors.CSHARP import Executor as CSharpExecutor


class Executor(CSharpExecutor):
    ext = 'fs'
    compiler_time_limit = 60  # fsc is slower than Roslyn
    # fsc looks at the file system type of its output folder (read-only, harmless); file copies
    # by descriptor are refused so .NET falls back to plain reads and writes.
    compiler_syscalls = CSharpExecutor.compiler_syscalls + ['fstatfs', 'statfs', ('copy_file_range', ACCESS_ENOSYS)]
    test_program = 'let line = stdin.ReadLine()\nprintfn "%s" line\n'

    @classmethod
    def fsharp_dir(cls):
        sdk = cls.latest(os.path.join(cls.dotnet_root(), 'sdk', '10.*'))
        return os.path.join(sdk, 'FSharp')

    def get_compile_args(self):
        root = self.dotnet_root()
        pack = self.latest(os.path.join(root, 'packs', 'Microsoft.NETCore.App.Ref', '10.*'))
        refs = sorted(glob.glob(os.path.join(pack, 'ref', 'net10.0', '*.dll')))
        fsharp = self.fsharp_dir()
        return [self.get_command(), os.path.join(fsharp, 'fsc.dll'),
                '--nologo', '--target:exe', '--optimize+', '--deterministic+', '--utf8output',
                '--noframework', '--simpleresolution', '--targetprofile:netcore', '--nowin32manifest',
                '--out:' + self.get_compiled_file(),
                '-r:' + os.path.join(fsharp, 'FSharp.Core.dll'),
                *['-r:' + ref for ref in refs], self._code]

    def compile(self):
        result = super().compile()
        # The program needs FSharp.Core next to it at run time.
        shutil.copy(os.path.join(self.fsharp_dir(), 'FSharp.Core.dll'), self._file('FSharp.Core.dll'))
        return result
