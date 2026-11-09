import json
import os
import shutil
import tempfile
from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings

from judge.management.commands.load_quizzes import DEFAULT_DIR
from judge.models import Quiz, QuizQuestion
from judge.models.tests.util import create_user
from judge.utils.quiz_scoring import build_key


class LoadQuizzesTest(TestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)
        media = override_settings(MEDIA_ROOT=self.media)
        media.enable()
        self.addCleanup(media.disable)

    def run_command(self, **kwargs):
        out = StringIO()
        call_command('load_quizzes', stdout=out, **kwargs)
        return out.getvalue()

    def test_no_author_does_nothing(self):
        self.assertIn('skipped', self.run_command(author='nobody-here'))
        self.assertFalse(Quiz.objects.exists())

    def test_loads_every_quiz_once_and_keeps_existing(self):
        create_user(username='samat1')
        expected = sorted(d for d in os.listdir(DEFAULT_DIR)
                          if os.path.isfile(os.path.join(DEFAULT_DIR, d, 'quiz.json')))
        self.assertGreaterEqual(len(expected), 9)
        self.run_command()
        self.assertEqual(sorted(Quiz.objects.values_list('key', flat=True)), expected)
        for quiz in Quiz.objects.all():
            self.assertEqual(quiz.access, Quiz.PUBLIC)
            self.assertTrue(quiz.cover)
            with open(os.path.join(DEFAULT_DIR, quiz.key, 'quiz.json'), encoding='utf-8') as f:
                self.assertEqual(quiz.questions.count(), len(json.load(f)['questions']), quiz.key)
        for question in QuizQuestion.objects.prefetch_related('options'):
            key = build_key(question)
            if question.type in ('single', 'code', 'truefalse'):
                self.assertEqual(len(key['correct']), 1, question)
            if question.type == 'multi':
                self.assertTrue(key['correct'], question)
        # A quiz edited or deleted on the site is never touched again.
        quiz = Quiz.objects.get(key='fizika')
        quiz.title = 'Изменено'
        quiz.is_deleted = True
        quiz.save()
        questions = QuizQuestion.objects.count()
        self.assertNotIn('added', self.run_command())
        self.assertEqual(QuizQuestion.objects.count(), questions)
        self.assertEqual(Quiz.objects.get(key='fizika').title, 'Изменено')
