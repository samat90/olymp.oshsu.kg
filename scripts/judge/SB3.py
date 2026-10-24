"""Scratch 3 for DMOJ (install in dmoj/executors as SB3.py: language keys are at most 6 characters),
run headless by scratch-run
(https://github.com/VNOI-Admin/scratch-run).

The site stores every submission as text, so a .sb3 project arrives base64-encoded
(the submit form does this when a .sb3 file is chosen). "ask and wait" reads a line of
input, "say" prints a line.
"""
import base64
import binascii
import io
import json
import zipfile

from dmoj.cptbox.filesystem_policies import ExactFile
from dmoj.cptbox.handlers import ACCESS_ENOSYS
from dmoj.error import CompileError
from dmoj.executors.script_executor import ScriptExecutor


def _test_project():
    # Smallest project that echoes one line: when flag clicked -> ask "" and wait -> say (answer).
    stage = {'isStage': True, 'name': 'Stage', 'variables': {}, 'lists': {}, 'broadcasts': {}, 'blocks': {},
             'comments': {}, 'currentCostume': 0, 'costumes': [], 'sounds': [], 'volume': 100, 'layerOrder': 0}
    blocks = {
        'a': {'opcode': 'event_whenflagclicked', 'next': 'b', 'parent': None, 'inputs': {}, 'fields': {},
              'shadow': False, 'topLevel': True, 'x': 0, 'y': 0},
        'b': {'opcode': 'sensing_askandwait', 'next': 'c', 'parent': 'a', 'inputs': {'QUESTION': [1, [10, '']]},
              'fields': {}, 'shadow': False, 'topLevel': False},
        'c': {'opcode': 'looks_say', 'next': None, 'parent': 'b', 'inputs': {'MESSAGE': [3, 'd', [10, '']]},
              'fields': {}, 'shadow': False, 'topLevel': False},
        'd': {'opcode': 'sensing_answer', 'next': None, 'parent': 'c', 'inputs': {}, 'fields': {},
              'shadow': False, 'topLevel': False},
    }
    sprite = {'isStage': False, 'name': 'Sprite1', 'variables': {}, 'lists': {}, 'broadcasts': {}, 'blocks': blocks,
              'comments': {}, 'currentCostume': 0, 'costumes': [], 'sounds': [], 'volume': 100, 'layerOrder': 1,
              'visible': True, 'x': 0, 'y': 0, 'size': 100, 'direction': 90, 'draggable': False,
              'rotationStyle': 'all around'}
    project = {'targets': [stage, sprite], 'monitors': [], 'extensions': [],
               'meta': {'semver': '3.0.0', 'vm': '0.2.0', 'agent': ''}}
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        z.writestr('project.json', json.dumps(project))
    return base64.b64encode(out.getvalue()).decode()


class Executor(ScriptExecutor):
    ext = 'sb3'
    command = 'scratch-run'
    nproc = -1  # scratch-run is a Go program and uses threads
    address_grace = 1024 * 1024
    data_grace = 524288
    fs = [ExactFile('/etc/ssl/openssl.cnf')]  # scratch-run is a packaged Node.js program
    syscalls = ['eventfd2', 'epoll_create1', 'epoll_ctl', 'epoll_wait', 'epoll_pwait', 'sched_yield',
                'getrandom', 'pipe2', 'futex', 'nanosleep', 'clock_nanosleep', 'capget',
                'shutdown', 'pkey_alloc', 'pkey_free', ('io_uring_setup', ACCESS_ENOSYS)]
    test_program = _test_project()

    def create_files(self, problem_id, source_code, *args, **kwargs):
        data = source_code
        if not data.startswith(b'PK'):
            try:
                data = base64.b64decode(b''.join(source_code.split()), validate=True)
            except (binascii.Error, ValueError):
                raise CompileError('Отправьте файл проекта Scratch (.sb3).\n')
        if not data.startswith(b'PK'):
            raise CompileError('Отправьте файл проекта Scratch (.sb3).\n')
        with open(self._code, 'wb') as f:
            f.write(data)

    def get_env(self):
        env = super().get_env()
        env['HOME'] = self._dir  # Node asks for a home folder at start-up
        return env

    def get_cmdline(self, **kwargs):
        return [self.get_command(), self._code]

    @classmethod
    def get_version_flags(cls, command):
        return ['--version']
