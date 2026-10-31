"""Add the ready-made public quizzes from scripts/content/quizzes/<key>/quiz.json to the site.

Purely additive: a quiz whose link key already exists (even deleted by its author) is skipped,
nothing is ever changed or removed. Runs after every deploy (scripts/deploy.sh).
"""
import json
import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from judge.models import Profile, Quiz, QuizOption, QuizQuestion
from judge.utils import quiz_images
from judge.utils.quiz_import import QuestionError, clean_question, problems

DEFAULT_DIR = os.path.join(settings.BASE_DIR, 'scripts', 'content', 'quizzes')


def upload(folder, name):
    with open(os.path.join(folder, name), 'rb') as f:
        return SimpleUploadedFile(name, f.read())


class Command(BaseCommand):
    help = 'Add the ready-made quizzes (only those not on the site yet).'

    def add_arguments(self, parser):
        parser.add_argument('--dir', default=DEFAULT_DIR)
        parser.add_argument('--author', default='samat1')

    def handle(self, *args, **options):
        root = options['dir']
        if not os.path.isdir(root):
            self.stdout.write('Quizzes: no folder %s' % root)
            return
        author = Profile.objects.filter(user__username=options['author']).first()
        if author is None:
            self.stdout.write('Quizzes: no user %s, skipped' % options['author'])
            return
        for name in sorted(os.listdir(root)):
            folder = os.path.join(root, name)
            path = os.path.join(folder, 'quiz.json')
            if not os.path.isfile(path):
                continue
            with open(path, encoding='utf-8') as f:
                spec = json.load(f)
            if Quiz.objects.filter(key=spec['key']).exists():
                continue
            with transaction.atomic():
                quiz = self.create(spec, folder, author)
            self.stdout.write('Quizzes: added «%s» (/quiz/%s/, %d questions)' %
                              (quiz.title, quiz.key, quiz.questions.count()))

    def create(self, spec, folder, author):
        quiz = Quiz.objects.create(author=author, title=spec['title'][:120], description=spec.get('description', ''),
                                   subject=spec.get('subject', '')[:60], theme=spec.get('theme', 'steppe'),
                                   access=Quiz.PUBLIC, key=spec['key'])
        if spec.get('cover'):
            quiz_images.store(quiz, 'cover', upload(folder, spec['cover']))
        for order, raw in enumerate(spec['questions']):
            try:
                fields, options = clean_question(raw)
            except QuestionError as e:
                raise CommandError('%s, question %d: %s' % (spec['key'], order + 1, e))
            found = problems(fields, options, bool(raw.get('image')))
            if found:
                raise CommandError('%s, question %d: %s' % (spec['key'], order + 1, '; '.join(found)))
            question = QuizQuestion.objects.create(quiz=quiz, order=order, **fields)
            if raw.get('image'):
                quiz_images.store(question, 'image', upload(folder, raw['image']))
            QuizOption.objects.bulk_create([
                QuizOption(question=question, order=i, text=o['text'], is_correct=o['is_correct'])
                for i, o in enumerate(options)])
        return quiz
