"""Add the ready-made courses from scripts/content/courses/<folder>/ to the site.

Purely additive: a course whose link key already exists is skipped (even if its author changed or deleted it),
nothing is ever changed or removed. Runs after every deploy (scripts/deploy.sh).

A course folder holds course.py (META: key, title, subject, language, description, ...) and files m*.py,
each defining MODULE = {'title': ..., 'lessons': [{'title', 'required', 'blocks': [...]}]}.
Block specs are dicts with a 'type': text, video, test, assignment, problem, file, image.
"""
import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from judge.models import Course, CourseBlock, CourseLesson, CourseModule, CourseOption, CourseQuestion, Problem, Profile
from judge.models.course import youtube_id

DEFAULT_DIR = os.path.join(settings.BASE_DIR, 'scripts', 'content', 'courses')


class CourseContentError(Exception):
    pass


def read_folder(folder):
    """(META, [MODULE, ...]) from a course folder."""
    scope = {}
    with open(os.path.join(folder, 'course.py'), encoding='utf-8') as f:
        exec(compile(f.read(), 'course.py', 'exec'), scope)
    modules = []
    for name in sorted(os.listdir(folder)):
        if re.fullmatch(r'm\d+\.py', name):
            part = {}
            with open(os.path.join(folder, name), encoding='utf-8') as f:
                exec(compile(f.read(), name, 'exec'), part)
            modules.append(part['MODULE'])
    return scope['META'], modules


def check_question(q, where):
    kind = q.get('type', CourseQuestion.SINGLE)
    options = q['options']
    answer = q['answer']
    if kind == CourseQuestion.SINGLE:
        if not isinstance(answer, int) or not 0 <= answer < len(options) or len(options) < 2:
            raise CourseContentError('%s: bad single question' % where)
    elif kind == CourseQuestion.MULTI:
        if not answer or any(not 0 <= a < len(options) for a in answer) or len(options) < 2:
            raise CourseContentError('%s: bad multi question' % where)
    elif kind in (CourseQuestion.NUMBER, CourseQuestion.TEXT):
        if not options:
            raise CourseContentError('%s: no accepted answers' % where)
    else:
        raise CourseContentError('%s: unknown type %s' % (where, kind))
    if not q['text'].strip():
        raise CourseContentError('%s: empty text' % where)


def question_text(q):
    """The question text; a code sample goes under it as a Markdown block."""
    if q.get('code'):
        return '%s\n\n```python\n%s\n```' % (q['text'], q['code'].rstrip('\n'))
    return q['text']


def validate(meta, modules):
    if not modules:
        raise CourseContentError('no modules')
    for mi, module in enumerate(modules, 1):
        for li, lesson in enumerate(module['lessons'], 1):
            for bi, block in enumerate(lesson['blocks'], 1):
                where = 'module %d lesson %d block %d' % (mi, li, bi)
                if block['type'] == 'video' and not youtube_id(block['video']):
                    raise CourseContentError('%s: bad video link' % where)
                if block['type'] == 'test':
                    for qi, q in enumerate(block['questions'], 1):
                        check_question(q, '%s question %d' % (where, qi))


class Command(BaseCommand):
    help = 'Add the ready-made courses (only those not on the site yet).'

    def add_arguments(self, parser):
        parser.add_argument('--dir', default=DEFAULT_DIR)
        parser.add_argument('--author', default='samat1')
        parser.add_argument('--only', default='', help='folder name of one course')

    def handle(self, *args, **options):
        root = options['dir']
        if not os.path.isdir(root):
            self.stdout.write('Courses: no folder %s' % root)
            return
        author = Profile.objects.filter(user__username=options['author']).first()
        if author is None:
            self.stdout.write('Courses: no user %s, skipped' % options['author'])
            return
        for name in sorted(os.listdir(root)):
            folder = os.path.join(root, name)
            if not os.path.isfile(os.path.join(folder, 'course.py')) or (options['only'] and options['only'] != name):
                continue
            meta, modules = read_folder(folder)
            validate(meta, modules)
            if Course.objects.filter(key=meta['key']).exists():
                self.stdout.write('Courses: %s is already on the site' % meta['key'])
                continue
            with transaction.atomic():
                self.create(author, meta, modules)
            self.stdout.write('Courses: added %s' % meta['key'])

    def create(self, author, meta, modules):
        if not author.is_teacher:
            Profile.objects.filter(id=author.id).update(is_teacher=True)
        course = Course.objects.create(
            author=author, key=meta['key'], title=meta['title'], subject=meta.get('subject', ''),
            language=meta.get('language', 'ru'), description=meta.get('description', ''), access=Course.PUBLIC,
            status=Course.PUBLISHED, sequential=meta.get('sequential', False),
            pass_percent=meta.get('pass_percent', 0), certificate=True, reviews_on=True)
        for mi, module in enumerate(modules):
            row = CourseModule.objects.create(course=course, title=module['title'], order=mi)
            for li, lesson in enumerate(module['lessons']):
                item = CourseLesson.objects.create(
                    course=course, module=row, order=li, title=lesson['title'],
                    is_required=lesson.get('required', True), mark_required=lesson.get('mark', True))
                for bi, block in enumerate(lesson['blocks']):
                    self.add_block(item, bi, block)

    def add_block(self, lesson, order, spec):
        kind = spec['type']
        block = CourseBlock(lesson=lesson, order=order, type=kind, title=spec.get('title', ''),
                            text=spec.get('text', ''), is_required=spec.get('required', kind == 'test'),
                            points=spec.get('points', 10), data=spec.get('data', {}))
        if kind == 'video':
            block.youtube_id = youtube_id(spec['video'])
        elif kind == 'problem':
            problem = Problem.objects.filter(code=spec['code'], is_public=True).first()
            if problem is None:
                self.stdout.write('Courses: problem %s is not public here, block skipped' % spec['code'])
                return
            block.problem = problem
            block.title = block.title or problem.name
            block.data = {'pass_percent': spec.get('pass_percent', 100)}
        elif kind == 'test':
            block.data = {'attempts': spec.get('attempts', 0), 'pass_percent': spec.get('pass_percent', 60),
                          'shuffle': spec.get('shuffle', False), 'show_answers': True}
        elif kind == 'assignment':
            block.data = {'allow_text': True, 'allow_file': spec.get('file', True), 'pass_percent': 0}
        block.save()
        if kind == 'test':
            for qi, q in enumerate(spec['questions']):
                self.add_question(block, qi, q)

    def add_question(self, block, order, q):
        kind = q.get('type', CourseQuestion.SINGLE)
        question = CourseQuestion.objects.create(
            block=block, order=order, type=kind, text=question_text(q), explanation=q.get('expl', ''),
            points=q.get('points', 1))
        answers = q['answer'] if isinstance(q['answer'], list) else [q['answer']]
        rows = []
        for i, text in enumerate(q['options']):
            correct = kind in (CourseQuestion.NUMBER, CourseQuestion.TEXT) or i in answers
            rows.append(CourseOption(question=question, order=i, text=str(text), is_correct=correct))
        CourseOption.objects.bulk_create(rows)
