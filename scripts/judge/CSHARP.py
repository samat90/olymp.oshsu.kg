"""Microsoft .NET 10 executor for DMOJ (install in dmoj/executors).

Roslyn is invoked directly: no MSBuild projects, NuGet restore, or user build
hooks. Both compilation and execution retain DMOJ's traced sandbox.
"""
import glob
import json
import os

from dmoj.cptbox.filesystem_policies import ExactFile
from dmoj.cptbox.handlers import ACCESS_EPERM
from dmoj.executors.compiled_executor import CompiledExecutor


def private_membarrier(debugger):
    # CoreCLR's write barrier only needs the calling process, never a global barrier.
    if debugger.uarg0 in (0, 8, 16):  # QUERY, PRIVATE_EXPEDITED, REGISTER_PRIVATE_EXPEDITED
        return True
    return ACCESS_EPERM(debugger)


class Executor(CompiledExecutor):
    ext = 'cs'
    command = 'dotnet'
    nproc = -1  # CoreCLR uses background threads, as do Mono and Java.
    address_grace = 16 * 1024 * 1024  # Virtual reservation; RSS is still limited.
    fsize = 64 * 1024 * 1024  # CoreCLR JIT uses memfd; disk writes remain denied.
    compiler_time_limit = 30
    fs = [ExactFile('/proc/self/status'), ExactFile('/proc/self/cgroup')]
    syscalls = ['memfd_create', 'ftruncate', 'fchmod', 'msync', 'clock_nanosleep', 'mincore',
                'getsid', ('membarrier', private_membarrier), ('mlock', ACCESS_EPERM),
                ('get_mempolicy', ACCESS_EPERM)]
    compiler_syscalls = ['getsid', 'mincore', ('membarrier', private_membarrier), ('mlock', ACCESS_EPERM),
                        ('get_mempolicy', ACCESS_EPERM)]
    test_program = 'using System; Console.WriteLine(Console.ReadLine());'

    @classmethod
    def dotnet_root(cls):
        return os.path.dirname(os.path.realpath(cls.get_command()))

    @classmethod
    def latest(cls, pattern):
        paths = glob.glob(pattern)
        if not paths:
            raise RuntimeError('Missing .NET 10 SDK/reference assemblies: ' + pattern)
        return max(paths, key=lambda p: tuple(int(n) for n in os.path.basename(p).split('.')))

    def create_files(self, problem_id, source_code, *args, **kwargs):
        super().create_files(problem_id, source_code, *args, **kwargs)
        config = {'runtimeOptions': {'tfm': 'net10.0', 'framework': {
            'name': 'Microsoft.NETCore.App', 'version': '10.0.0'},
            'configProperties': {'System.GC.Server': False}}}
        with open(self._file(problem_id + '.runtimeconfig.json'), 'w') as f:
            json.dump(config, f)

    def get_compile_args(self):
        root = self.dotnet_root()
        sdk = self.latest(os.path.join(root, 'sdk', '10.*'))
        pack = self.latest(os.path.join(root, 'packs', 'Microsoft.NETCore.App.Ref', '10.*'))
        refs = sorted(glob.glob(os.path.join(pack, 'ref', 'net10.0', '*.dll')))
        return [self.get_command(), os.path.join(sdk, 'Roslyn', 'bincore', 'csc.dll'),
                '-nologo', '-noconfig', '-nostdlib+', '-target:exe', '-optimize+',
                '-langversion:14', '-utf8output', '-deterministic+',
                '-out:' + self.get_compiled_file(),
                *['-r:' + ref for ref in refs], self._code]

    def get_compiled_file(self):
        return self._file(self.problem + '.dll')

    def get_executable(self):
        return self.get_command()

    def get_cmdline(self, **kwargs):
        return [self.get_command(), self._executable]

    def get_env(self):
        env = super().get_env()
        env.update({'HOME': self._dir, 'DOTNET_ROOT': self.dotnet_root(), 'DOTNET_EnableDiagnostics': '0',
                    'DOTNET_CLI_TELEMETRY_OPTOUT': '1', 'DOTNET_SKIP_FIRST_TIME_EXPERIENCE': '1',
                    'DOTNET_GCHeapHardLimit': format(getattr(self, '_heap_limit', 256 * 1024 * 1024), 'x'),
                    'DOTNET_GCConserveMemory': '9', 'DOTNET_gcServer': '0',
                    'DOTNET_PROCESSOR_COUNT': '1'})
        return env

    def get_compile_env(self):
        return self.get_env()

    def launch(self, *args, **kwargs):
        self._heap_limit = max(kwargs.get('memory', 262144), 16384) * 1024
        return super().launch(*args, **kwargs)

    @classmethod
    def get_version_flags(cls, command):
        return ['--version']
