from importlib import import_module
from io import StringIO
from types import SimpleNamespace

from django.apps import apps
from django.core.management import call_command
from django.db import connection
from django.test import TestCase

from judge.models import Language, LanguageLimit, Submission
from judge.models.tests.util import create_problem, create_user


class ModernCSharpTests(TestCase):
    def test_enable_csharp_for_every_problem_preserves_other_languages(self):
        migration = import_module('judge.migrations.0154_csharp_all_problems')
        modern, _ = Language.objects.get_or_create(key='CSHARP', defaults={'name': 'C# (.NET 10)'})
        python, _ = Language.objects.get_or_create(key='PY3', defaults={'name': 'Python 3'})
        existing = create_problem(code='alreadycsharp', allowed_languages=['CSHARP'])
        other = create_problem(code='pythononly', allowed_languages=['PY3'])
        empty = create_problem(code='nolanguages')
        editor = SimpleNamespace(connection=connection)
        migration.enable_csharp(apps, editor)
        migration.enable_csharp(apps, editor)
        self.assertEqual(set(existing.allowed_languages.all()), {modern})
        self.assertEqual(set(other.allowed_languages.all()), {modern, python})
        self.assertEqual(set(empty.allowed_languages.all()), {modern})

    def test_upgrade_preserves_history_limits_and_restricted_problems(self):
        migration = import_module('judge.migrations.0153_modern_csharp')
        mono = Language.objects.create(key='MONOCS', name='C# (Mono)', common_name='C#')
        problem = create_problem(code='csharpupgrade', allowed_languages=['MONOCS'])
        restricted = create_problem(code='nocsharp')
        user = create_user(username='csharpuser')
        user.profile.language = mono
        user.profile.save()
        submission = Submission.objects.create(user=user.profile, problem=problem, language=mono)
        LanguageLimit.objects.create(problem=problem, language=mono, time_limit=3, memory_limit=131072)
        editor = SimpleNamespace(connection=connection)

        migration.modern_csharp(apps, editor)
        migration.modern_csharp(apps, editor)  # Safe to apply to an already provisioned runtime.
        modern = Language.objects.get(key='CSHARP')
        self.assertEqual(list(problem.allowed_languages.all()), [modern])
        self.assertFalse(restricted.allowed_languages.exists())
        limit = LanguageLimit.objects.get(problem=problem, language=modern)
        self.assertEqual((limit.time_limit, limit.memory_limit), (3, 131072))
        submission.refresh_from_db()
        user.profile.refresh_from_db()
        self.assertEqual(submission.language_id, mono.pk)
        self.assertEqual(user.profile.language_id, modern.pk)

        migration.restore_mono(apps, editor)
        self.assertEqual(list(problem.allowed_languages.all()), [mono])
        self.assertTrue(Language.objects.filter(pk=modern.pk).exists())

    def test_seed_fixture_reuses_language_by_key(self):
        modern, _ = Language.objects.get_or_create(key='CSHARP', defaults={'name': 'C# (.NET 10)'})
        call_command('loaddata', 'language_small', stdout=StringIO())
        call_command('loaddata', 'language_small', stdout=StringIO())
        self.assertEqual(Language.objects.get(key='CSHARP').pk, modern.pk)
