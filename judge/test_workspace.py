import base64
import json

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from judge.models import Judge, Language, WorkspaceFile
from judge.models.tests.util import create_contest, create_contest_participation, create_contest_problem, \
    create_problem, create_user
from judge.utils.problem_samples import extract_samples


@override_settings(DMOJ_RUNNER_PUBLIC_URL='http://runner.test', DMOJ_RUNNER_SECRET='0123456789abcdef0123456789')
class WorkspaceTest(TestCase):
    fixtures = ['language_small.json']

    def setUp(self):
        self.user = create_user(username='ws_user')
        self.other = create_user(username='ws_other')
        for user in (self.user, self.other):
            user.set_password('ws-pass-123')
            user.save()
        judge = Judge.objects.create(name='ws_judge', auth_key='k' * 20, online=True)
        judge.runtimes.set(Language.objects.all())
        self.client.login(username='ws_user', password='ws-pass-123')

    def post(self, name, data=None, *args):
        response = self.client.post(reverse(name, args=args), json.dumps(data or {}), content_type='application/json')
        return response, response.json()

    def test_create_save_rename_move_delete(self):
        _, folder = self.post('workspace_api_create', {'name': 'lab1', 'folder': True})
        self.assertTrue(folder['ok'])
        _, file = self.post('workspace_api_create', {'name': 'a.py', 'parent': folder['file']['id']})
        self.assertTrue(file['ok'])
        self.assertEqual(file['file']['language'], 'PY3')
        fid = file['file']['id']

        _, saved = self.post('workspace_api_save', {'content': 'print(1)', 'stdin': '5'}, fid)
        self.assertTrue(saved['ok'])
        self.assertEqual(WorkspaceFile.objects.get(id=fid).content, 'print(1)')

        _, dup = self.post('workspace_api_create', {'name': 'a.py', 'parent': folder['file']['id']})
        self.assertFalse(dup['ok'])

        _, renamed = self.post('workspace_api_rename', {'name': 'main.cpp'}, fid)
        self.assertEqual(renamed['file']['language'], 'CPP17')

        _, moved = self.post('workspace_api_move', {'parent': None}, fid)
        self.assertIsNone(moved['file']['parent'])

        _, loop = self.post('workspace_api_move', {'parent': folder['file']['id']}, folder['file']['id'])
        self.assertFalse(loop['ok'])

        listing = self.client.get(reverse('workspace_api_list')).json()
        self.assertEqual(len(listing['files']), 2)

        self.post('workspace_api_delete', {}, folder['file']['id'])
        self.assertEqual(WorkspaceFile.objects.filter(owner=self.user.profile).count(), 1)

    def test_bad_names(self):
        for name in ['', '..', 'a/b', 'x' * 101, 'bad\\name']:
            _, data = self.post('workspace_api_create', {'name': name})
            self.assertFalse(data['ok'], name)

    def test_cannot_touch_other_users_files(self):
        file = WorkspaceFile.objects.create(owner=self.other.profile, name='secret.py', content='x')
        response = self.client.get(reverse('workspace_api_get', args=(file.id,)))
        self.assertEqual(response.status_code, 404)
        response, _ = self.client.post(reverse('workspace_api_delete', args=(file.id,))), None
        self.assertEqual(response.status_code, 404)
        self.assertTrue(WorkspaceFile.objects.filter(id=file.id).exists())

    def test_share_and_fork(self):
        _, file = self.post('workspace_api_create', {'name': 'share.py', 'content': 'print(42)'})
        _, shared = self.post('workspace_api_share', {'on': True}, file['file']['id'])
        key = shared['file']['share_key']
        self.assertTrue(key)
        self.client.logout()
        page = self.client.get(reverse('workspace_shared', args=(key,)))
        self.assertContains(page, 'share.py')
        self.client.login(username='ws_other', password='ws-pass-123')
        _, forked = self.post('workspace_api_fork', {}, key)
        self.assertTrue(forked['ok'])
        self.assertEqual(WorkspaceFile.objects.get(id=forked['file']['id']).owner, self.other.profile)

    def test_file_limit(self):
        with self.settings():
            from judge.models import workspace
            old = workspace.MAX_FILES_PER_USER
            try:
                import judge.views.workspace as views
                views.MAX_FILES_PER_USER = 2
                self.post('workspace_api_create', {'name': '1.py'})
                self.post('workspace_api_create', {'name': '2.py'})
                _, data = self.post('workspace_api_create', {'name': '3.py'})
                self.assertFalse(data['ok'])
            finally:
                views.MAX_FILES_PER_USER = old

    def test_runner_token(self):
        _, data = self.post('runner_token', {})
        self.assertTrue(data['ok'])
        body = data['token'].split('.')[0]
        payload = json.loads(base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)))
        self.assertEqual(payload['u'], self.user.id)
        self.assertIn('PY3', payload['langs'])

    def test_runner_token_for_problem_uses_its_limits(self):
        problem = create_problem(code='wsprob', time_limit=1.5, memory_limit=131072, is_public=True)
        problem.allowed_languages.set(Language.objects.filter(key='PY3'))
        _, data = self.post('runner_token', {'problem': problem.code})
        body = data['token'].split('.')[0]
        payload = json.loads(base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)))
        self.assertEqual(payload['langs'], ['PY3'])
        self.assertEqual(payload['time'], 1.5)
        self.assertEqual(payload['memory'], 131072)

    def test_sandbox_closed_during_contest(self):
        now = timezone.now()
        contest = create_contest(key='wscontest', start_time=now - timezone.timedelta(hours=1),
                                 end_time=now + timezone.timedelta(hours=1), is_visible=True)
        problem = create_problem(code='wsin', is_public=False)
        other_problem = create_problem(code='wsout', is_public=True)
        create_contest_problem(contest=contest, problem=problem)
        participation = create_contest_participation(contest=contest, user=self.user.profile)
        profile = self.user.profile
        profile.current_contest = participation
        profile.save()

        _, data = self.post('runner_token', {})
        self.assertFalse(data['ok'])
        _, data = self.post('runner_token', {'problem': other_problem.code})
        self.assertFalse(data['ok'])
        _, data = self.post('runner_token', {'problem': problem.code})
        self.assertTrue(data['ok'])
        _, data = self.post('workspace_api_create', {'name': 'x.py'})
        self.assertFalse(data['ok'])
        self.assertTrue(other_problem.is_public)


class SampleExtractionTest(TestCase):
    def test_site_format(self):
        md = '## Пример\n\n**Ввод**\n\n```\n5\n```\n\n**Вывод**\n\n```\n15\n```\n'
        self.assertEqual(extract_samples(md), [{'input': '5\n', 'output': '15\n'}])

    def test_headings_and_several_samples(self):
        md = ('### Пример 1\n#### Входные данные\n```\n1 2\n```\n#### Выходные данные:\n```\n3\n```\n'
              '### Пример 2\n**Sample Input**\n~~~\n4 5\n~~~\n**Sample Output**\n~~~\n9\n~~~\n')
        self.assertEqual(extract_samples(md), [{'input': '1 2\n', 'output': '3\n'},
                                               {'input': '4 5\n', 'output': '9\n'}])

    def test_code_blocks_without_labels_are_ignored(self):
        md = 'Пример кода:\n```\nint main() {}\n```\n'
        self.assertEqual(extract_samples(md), [])
