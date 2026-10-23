import tempfile
from io import StringIO
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import skipUnless
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.core.management import call_command
from django.db import close_old_connections, connection
from django.test import RequestFactory, TestCase, TransactionTestCase, override_settings

from judge.models import Problem, ProblemGroup


@override_settings(SECURE_SSL_REDIRECT=False)
class ProblemCodeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.group = ProblemGroup.objects.create(name='numbers', full_name='Numbers')

    def make_problem(self, **kwargs):
        return Problem.objects.create(group=self.group, name='Task', description='Statement',
                                      time_limit=1, memory_limit=65536, points=100, **kwargs)

    @override_settings(DMOJ_NUMERIC_PROBLEM_CODES=True)
    def test_creation_assigns_number_and_ignores_supplied_code(self):
        first = self.make_problem(code='bad-name')
        second = self.make_problem()
        self.assertEqual(first.code, '%06d' % first.pk)
        self.assertEqual(second.code, '%06d' % second.pk)
        self.assertNotEqual(first.code, second.code)
        first.name = 'Updated'
        first.save()
        first.save()
        self.assertEqual(Problem.objects.get(pk=first.pk).code, first.code)

    @override_settings(DMOJ_NUMERIC_PROBLEM_CODES=True)
    def test_existing_number_cannot_be_changed(self):
        problem = self.make_problem()
        problem.code = '999999'
        with self.assertRaises(ValidationError):
            problem.save()

    @override_settings(DMOJ_NUMERIC_PROBLEM_CODES=True)
    def test_cloning_does_not_move_original_test_data(self):
        problem = self.make_problem()
        original = problem.code
        problem.pk = None
        with patch('judge.models.problem_data.ProblemData._update_code') as rename:
            problem.save()
        rename.assert_not_called()
        self.assertNotEqual(problem.code, original)
        self.assertTrue(Problem.objects.filter(code=original).exists())

    @override_settings(DMOJ_NUMERIC_PROBLEM_CODES=True)
    def test_range_exhaustion_rolls_back_insert(self):
        with self.assertRaises(ValidationError):
            self.make_problem(pk=1000000)
        self.assertFalse(Problem.objects.filter(pk=1000000).exists())

    @override_settings(DMOJ_NUMERIC_PROBLEM_CODES=True)
    def test_management_creation_assigns_number(self):
        from judge.models import ProblemType
        topic = ProblemType.objects.create(name='numbers', full_name='Numbers')
        output = StringIO()
        call_command('create_problem', 'ignored', 'New task', 'Statement', topic.name, self.group.name,
                     stdout=output)
        problem = Problem.objects.get(name='New task')
        self.assertEqual(problem.code, '%06d' % problem.pk)
        self.assertEqual(output.getvalue().strip(), problem.code)

    def test_old_urls_preserve_suffix_query_and_post_body(self):
        from judge.middleware import ProblemCodeAliasMiddleware
        from judge.models import ProblemCodeAlias
        problem = self.make_problem(code='000123', is_public=True)
        ProblemCodeAlias.objects.create(code='old-task', problem=problem)
        middleware = ProblemCodeAliasMiddleware(lambda request: None)
        factory = RequestFactory()
        request = factory.get('/problem/old-task/submissions/?page=2')
        request.user = AnonymousUser()
        kwargs = {'problem': 'old-task'}
        response = middleware.process_view(request, lambda: None, (), kwargs)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], '/problem/000123/submissions/?page=2')
        request = factory.post('/problem/old-task/submit', {'source': 'print(42)'})
        request.user = AnonymousUser()
        kwargs = {'problem': 'old-task'}
        self.assertIsNone(middleware.process_view(request, lambda: None, (), kwargs))
        self.assertEqual(kwargs['problem'], '000123')
        self.assertEqual(request.POST['source'], 'print(42)')

    def test_old_private_url_does_not_disclose_task(self):
        from judge.middleware import ProblemCodeAliasMiddleware
        from judge.models import ProblemCodeAlias
        problem = self.make_problem(code='000124', is_public=False)
        ProblemCodeAlias.objects.create(code='private-old', problem=problem)
        request = RequestFactory().get('/problem/private-old')
        request.user = AnonymousUser()
        kwargs = {'problem': 'private-old'}
        response = ProblemCodeAliasMiddleware(lambda request: None).process_view(request, lambda: None, (), kwargs)
        self.assertEqual(response.status_code, 404)

    def test_actual_routes_use_alias_and_keep_private_data_protected(self):
        from judge.models import ProblemCodeAlias
        public = self.make_problem(code='000125', is_public=True)
        private = self.make_problem(code='000126', is_public=False)
        ProblemCodeAlias.objects.create(code='public-old', problem=public)
        ProblemCodeAlias.objects.create(code='secret-old', problem=private)
        for suffix in ('', '/submit', '/rank/', '/submissions/', '/pdf', '/test_data'):
            response = self.client.get('/problem/public-old' + suffix, {'page': 2})
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response['Location'], '/problem/000125' + suffix + '?page=2')
        self.assertEqual(self.client.get('/problem/secret-old/data/tests.zip').status_code, 404)
        response = self.client.get('/problem/000126/data/tests.zip')
        self.assertIn(response.status_code, (302, 404))
        if response.status_code == 302:
            self.assertTrue(response['Location'].startswith('/accounts/login/'))

    def test_numeric_and_reserved_word_old_codes_are_resolved(self):
        from judge.models import ProblemCodeAlias
        public = self.make_problem(code='000127', is_public=True)
        for old in ('123456', 'problem'):
            ProblemCodeAlias.objects.create(code=old, problem=public)
            response = self.client.get('/problem/' + old)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response['Location'], '/problem/000127')

    def test_migration_preserves_files_and_can_rollback_and_resume(self):
        from judge.models import ProblemCodeAlias, ProblemData
        from judge.utils.problem_codes import apply_plan, build_plan
        from judge.utils.problem_code_storage import directory_digest
        problem = self.make_problem(code='legacy-task', is_public=True)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / problem.code
            old.mkdir()
            (old / 'tests.zip').write_bytes(b'original archive')
            (old / 'init.yml').write_text('archive: tests.zip\n')
            ProblemData.objects.create(problem=problem, zipfile='legacy-task/tests.zip')
            before = directory_digest(old)
            plan = build_plan(root)
            cache.set('numbering-session-marker', 'session-preserved', 300)
            apply_plan(plan, root)
            self.assertEqual(cache.get('numbering-session-marker'), 'session-preserved')
            new = '%06d' % problem.pk
            self.assertEqual(directory_digest(root / new), before)
            self.assertEqual(ProblemData.objects.get(problem=problem).zipfile.name, new + '/tests.zip')
            self.assertEqual(ProblemCodeAlias.objects.get(code='legacy-task').problem_id, problem.pk)
            apply_plan(plan, root)
            apply_plan(plan, root, rollback=True)
            self.assertEqual(Problem.objects.get(pk=problem.pk).code, 'legacy-task')
            self.assertEqual(directory_digest(old), before)
            self.assertFalse(ProblemCodeAlias.objects.filter(code='legacy-task').exists())
            apply_plan(plan, root)
            self.assertEqual(Problem.objects.get(pk=problem.pk).code, new)

    def test_file_conflict_stops_before_database_change(self):
        from judge.utils.problem_codes import apply_plan, build_plan
        problem = self.make_problem(code='conflict-old')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / problem.code).mkdir()
            plan = build_plan(root)
            (root / ('%06d' % problem.pk)).mkdir()
            with self.assertRaises(ValueError):
                apply_plan(plan, root)
            self.assertEqual(Problem.objects.get(pk=problem.pk).code, problem.code)


    def test_migration_failure_restores_renamed_directory(self):
        from judge.utils.problem_codes import apply_plan, build_plan
        problem = self.make_problem(code='failure-old')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / problem.code).mkdir()
            plan = build_plan(root)
            with patch('judge.utils.problem_codes.update_records', side_effect=RuntimeError('failure')):
                with self.assertRaises(RuntimeError):
                    apply_plan(plan, root)
            self.assertTrue((root / problem.code).is_dir())
            self.assertFalse((root / ('%06d' % problem.pk)).exists())
            self.assertEqual(Problem.objects.get(pk=problem.pk).code, problem.code)


@skipUnless(connection.vendor == 'postgresql', 'Concurrent sequence test requires PostgreSQL')
@override_settings(DMOJ_NUMERIC_PROBLEM_CODES=True)
class ConcurrentProblemCodeTests(TransactionTestCase):
    def test_twenty_parallel_creations_have_unique_persistent_numbers(self):
        group = ProblemGroup.objects.create(name='parallel-numbers', full_name='Parallel')

        def create(index):
            close_old_connections()
            try:
                problem = Problem.objects.create(name='Task %s' % index, description='Statement',
                                                 group_id=group.pk, time_limit=1, memory_limit=65536, points=100)
                return problem.pk, problem.code
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=8) as pool:
            result = list(pool.map(create, range(20)))
        self.assertEqual(len({code for _, code in result}), 20)
        self.assertTrue(all(code == '%06d' % pk for pk, code in result))
