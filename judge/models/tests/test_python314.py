from importlib import import_module
from types import SimpleNamespace

from django.apps import apps
from django.db import connection
from django.test import TestCase

from judge.models import Language, Submission
from judge.models.tests.util import create_problem, create_user


class PythonUpgradeTests(TestCase):
    def test_upgrade_keeps_language_identity_history_and_other_languages(self):
        migration = import_module('judge.migrations.0155_python314')
        python, _ = Language.objects.get_or_create(key='PY3', defaults={'name': 'Python 3'})
        csharp, _ = Language.objects.get_or_create(key='CSHARP', defaults={'name': 'C#'})
        existing = create_problem(code='pythonexisting', allowed_languages=['PY3'])
        restricted = create_problem(code='pythonrestricted', allowed_languages=['CSHARP'])
        user = create_user(username='pythonupgrade')
        submission = Submission.objects.create(user=user.profile, problem=existing, language=python)
        editor = SimpleNamespace(connection=connection)
        migration.upgrade_python(apps, editor)
        migration.upgrade_python(apps, editor)
        python.refresh_from_db()
        submission.refresh_from_db()
        self.assertEqual(python.name, 'Python 3.14')
        python._meta.get_field('short_name').clean(python.short_name, python)
        self.assertEqual(submission.language_id, python.pk)
        self.assertEqual(set(existing.allowed_languages.all()), {python})
        self.assertEqual(set(restricted.allowed_languages.all()), {python, csharp})
        migration.restore_label(apps, editor)
        python.refresh_from_db()
        self.assertEqual(python.name, 'Python 3')
        self.assertTrue(Submission.objects.filter(pk=submission.pk, language=python).exists())
