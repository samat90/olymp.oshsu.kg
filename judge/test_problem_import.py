import io
import os
import shutil
import tempfile
import zipfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from judge.models import Language, Problem, problem_data_storage
from judge.models.tests.util import create_problem_group, create_user
from judge.utils.problem_import import parse_statement, read_upload
from judge.utils.test_files import pair_test_files

TEMPLATE = os.path.join(settings.BASE_DIR, 'resources', 'problem-template.md')


def make_zip(files):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return out.getvalue()


class ParserTest(TestCase):
    def test_template(self):
        with open(TEMPLATE, encoding='utf-8') as f:
            parsed = parse_statement(f.read(), 'problem-template.md')
        self.assertEqual(parsed.name, 'Сумма двух чисел')
        self.assertEqual(parsed.time_limit, 1)
        self.assertEqual(parsed.memory_limit, 262144)
        self.assertEqual(len(parsed.samples), 2)
        self.assertEqual(parsed.tests, [(b'1 1\n', b'2\n'), (b'-1000000000 -1000000000\n', b'-2000000000\n')])
        self.assertNotIn('Тесты', parsed.description)
        self.assertNotIn('# Сумма', parsed.description)
        self.assertIn('## Пояснение', parsed.description)

    def test_limits_in_other_units(self):
        parsed = parse_statement('Ограничение по времени: 500 мс\nОграничение по памяти: 64 MB\n\nТекст', 'x.txt')
        self.assertEqual((parsed.time_limit, parsed.memory_limit), (0.5, 65536))
        parsed = parse_statement('Time limit: 2 s\nMemory limit: 1 GB\n\nText', 'two-sum.md')
        self.assertEqual((parsed.time_limit, parsed.memory_limit, parsed.name), (2, 1048576, 'two-sum'))

    def test_statement_inside_zip_and_samples_as_fallback(self):
        statement = 'Найдите сумму.\n\n## Пример\n\nВход:\n```\n1 2\n```\n\nВыход:\n```\n3\n```\n'
        parsed = read_upload('', None, make_zip({'Задача - Сумма/условие.txt': statement.encode('cp1251')}))
        self.assertEqual(parsed.name, 'Сумма')
        self.assertEqual(parsed.tests_source, 'samples')
        self.assertEqual(parsed.tests, [(b'1 2\n', b'3\n')])

    def test_nested_tests_zip(self):
        inner = make_zip({'01.in': '1', '01.out': '2', '02.in': '3', '02.out': '4'})
        parsed = read_upload('a.md', '# A\n\nТекст'.encode(), make_zip({'tests.zip': inner}))
        self.assertEqual(parsed.tests_source, 'archive')
        self.assertEqual(len(parsed.tests), 2)

    def test_pairing(self):
        self.assertEqual(pair_test_files(['10.in', '10.out', '9.in', '9.out', 'x.txt']),
                         [('9.in', '9.out'), ('10.in', '10.out')])


class ImportViewTest(TestCase):
    fixtures = ['language_small.json']

    def setUp(self):
        create_problem_group('group')
        admin = create_user(username='imp_admin', is_superuser=True, is_staff=True)
        admin.set_password('imp-pass-1')
        admin.save()
        self.client.login(username='imp_admin', password='imp-pass-1')

    def use_temp_storage(self):
        """Write test data to a temporary folder, never to the real problems folder."""
        tmp = tempfile.mkdtemp()
        old = problem_data_storage._location
        for attr in ('base_location', 'location'):
            problem_data_storage.__dict__.pop(attr, None)
        problem_data_storage._location = tmp

        def restore():
            problem_data_storage._location = old
            for attr in ('base_location', 'location'):
                problem_data_storage.__dict__.pop(attr, None)
            shutil.rmtree(tmp, ignore_errors=True)
        self.addCleanup(restore)
        return tmp

    @override_settings(DMOJ_NUMERIC_PROBLEM_CODES=True)
    def test_full_import(self):
        root = self.use_temp_storage()
        with open(TEMPLATE, 'rb') as f:
            statement = SimpleUploadedFile('problem-template.md', f.read())
        archive = SimpleUploadedFile('tests.zip', make_zip({
            '1.in': '1 2\n', '1.out': '3\n', '2.in': '5 5\n', '2.out': '10\n', '3.in': '0 0\n', '3.out': '0\n',
        }))
        page = self.client.post(reverse('admin_import_problem'), {'statement': statement, 'archive': archive})
        self.assertContains(page, 'Сумма двух чисел')
        token = page.context['review'].initial['token']
        response = self.client.post(reverse('admin_import_problem'), {
            'token': token, 'name': 'Сумма двух чисел', 'time_limit': 1, 'memory_mb': 256, 'points': 100,
            'description': page.context['review'].initial['description'],
        })
        problem = Problem.objects.get(name='Сумма двух чисел')
        self.assertRedirects(response, reverse('admin:judge_problem_change', args=(problem.id,)),
                             fetch_redirect_response=False)
        self.assertRegex(problem.code, r'^\d{6}$')
        self.assertEqual(problem.cases.count(), 3)
        self.assertEqual(problem.allowed_languages.count(), Language.objects.count())
        with open(os.path.join(root, problem.code, 'init.yml')) as f:
            self.assertIn('01.in', f.read())
