"""Add the ready-made courses from scripts/content/courses/<folder>/ to the site.

A course whose link key is not on the site yet is added. A course that is already there is left alone, unless the
folder holds a newer content version (META['version'] is greater than the version recorded in the misc config
item `course_version:<key>`): then the texts are refreshed in place. Modules, lessons, blocks and questions are
matched by position, so progress, attempts and works of learners stay attached. Course settings, and lessons or
blocks added by teachers, are never touched or removed. Runs after every deploy (scripts/deploy.sh).

A course folder holds course.py (META: key, title, subject, language, lang, version, description, ...) and files
m*.py, each defining MODULE = {'title': ..., 'lessons': [{'title', 'required', 'blocks': [...]}]}.
The shared helpers in ../_dsl.py are available in all of them. Block specs are dicts with a 'type': text, video,
test, assignment, problem, file, image.
"""
import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from judge.models import Course, CourseBlock, CourseLesson, CourseModule, CourseOption, CourseQuestion, MiscConfig, \
    Problem, Profile
from judge.models.course import youtube_id

DEFAULT_DIR = os.path.join(settings.BASE_DIR, 'scripts', 'content', 'courses')
MODULE_FILE = re.compile(r'm[0-9]+\.py')


class CourseContentError(Exception):
    pass


def read_folder(folder):
    """(META, [MODULE, ...]) from a course folder."""
    base = {}
    dsl = os.path.join(os.path.dirname(folder), '_dsl.py')
    if os.path.isfile(dsl):
        with open(dsl, encoding='utf-8') as f:
            exec(compile(f.read(), '_dsl.py', 'exec'), base)
    scope = dict(base)
    with open(os.path.join(folder, 'course.py'), encoding='utf-8') as f:
        exec(compile(f.read(), 'course.py', 'exec'), scope)
    modules = []
    for name in sorted(os.listdir(folder)):
        if MODULE_FILE.fullmatch(name):
            part = dict(base)
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


def question_text(q, lang='python'):
    """The question text; a code sample goes under it as a Markdown block."""
    if q.get('code'):
        return '%s\n\n```%s\n%s\n```' % (q['text'], lang, q['code'].rstrip('\n'))
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


def version_key(key):
    return 'course_version:%s' % key


def stored_version(key):
    value = MiscConfig.objects.filter(key=version_key(key)).values_list('value', flat=True).first()
    return int(value) if value and value.isdigit() else None


def store_version(key, version):
    MiscConfig.objects.update_or_create(key=version_key(key), defaults={'value': str(version)})


class Command(BaseCommand):
    help = 'Add the ready-made courses (only those not on the site yet) and refresh them when the content is newer.'

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
            version = meta.get('version', 1)
            course = Course.objects.filter(key=meta['key']).first()
            if course is None:
                with transaction.atomic():
                    self.create(author, meta, modules)
                    store_version(meta['key'], version)
                self.stdout.write('Courses: added %s' % meta['key'])
            elif (stored_version(meta['key']) or 1) < version:
                with transaction.atomic():
                    changed = self.refresh(course, meta, modules)
                    store_version(meta['key'], version)
                self.stdout.write('Courses: %s refreshed to version %d (%d items)' % (meta['key'], version, changed))
            else:
                self.stdout.write('Courses: %s is already on the site' % meta['key'])

    # ------------------------------------------------------------ create

    def create(self, author, meta, modules):
        if not author.is_teacher:
            Profile.objects.filter(id=author.id).update(is_teacher=True)
        course = Course.objects.create(
            author=author, key=meta['key'], title=meta['title'], subject=meta.get('subject', ''),
            language=meta.get('language', 'ru'), description=meta.get('description', ''), access=Course.PUBLIC,
            status=Course.PUBLISHED, sequential=meta.get('sequential', False),
            pass_percent=meta.get('pass_percent', 0), certificate=True, reviews_on=True, auto_mode=True)
        lang = meta.get('lang', 'python')
        for mi, module in enumerate(modules):
            row = CourseModule.objects.create(course=course, title=module['title'], order=mi)
            for li, lesson in enumerate(module['lessons']):
                item = CourseLesson.objects.create(
                    course=course, module=row, order=li, title=lesson['title'],
                    is_required=lesson.get('required', True), mark_required=lesson.get('mark', True))
                for bi, block in enumerate(lesson['blocks']):
                    self.add_block(item, bi, block, lang)

    def block_fields(self, spec, lang):
        kind = spec['type']
        fields = {'title': spec.get('title', ''), 'text': spec.get('text', ''),
                  'points': spec.get('points', 10), 'data': spec.get('data', {})}
        if kind == 'video':
            fields['youtube_id'] = youtube_id(spec['video'])
        elif kind == 'problem':
            fields['data'] = {'pass_percent': spec.get('pass_percent', 100)}
        elif kind == 'test':
            fields['data'] = {'attempts': spec.get('attempts', 0), 'pass_percent': spec.get('pass_percent', 60),
                              'shuffle': spec.get('shuffle', False), 'show_answers': True}
        elif kind == 'assignment':
            fields['data'] = {'allow_text': True, 'allow_file': spec.get('file', True), 'pass_percent': 0}
        return fields

    def add_block(self, lesson, order, spec, lang):
        kind = spec['type']
        fields = self.block_fields(spec, lang)
        block = CourseBlock(lesson=lesson, order=order, type=kind, is_required=spec.get('required', kind == 'test'),
                            **fields)
        if kind == 'problem':
            problem = Problem.objects.filter(code=spec['code'], is_public=True).first()
            if problem is None:
                self.stdout.write('Courses: problem %s is not public here, block skipped' % spec['code'])
                return
            block.problem = problem
            block.title = block.title or problem.name
        block.save()
        if kind == 'test':
            for qi, q in enumerate(spec['questions']):
                self.add_question(block, qi, q, lang)

    def add_question(self, block, order, q, lang):
        kind = q.get('type', CourseQuestion.SINGLE)
        question = CourseQuestion.objects.create(
            block=block, order=order, type=kind, text=question_text(q, lang), explanation=q.get('expl', ''),
            points=q.get('points', 1))
        self.add_options(question, q)

    def add_options(self, question, q):
        kind = q.get('type', CourseQuestion.SINGLE)
        answers = q['answer'] if isinstance(q['answer'], list) else [q['answer']]
        rows = []
        for i, text in enumerate(q['options']):
            correct = kind in (CourseQuestion.NUMBER, CourseQuestion.TEXT) or i in answers
            rows.append(CourseOption(question=question, order=i, text=str(text), is_correct=correct))
        CourseOption.objects.bulk_create(rows)

    # ------------------------------------------------------------ refresh

    def refresh(self, course, meta, modules):
        """Update texts in place by position. Returns the number of changed items."""
        lang = meta.get('lang', 'python')
        changed = 0
        if meta.get('description') and course.description != meta['description']:
            course.description = meta['description']
            course.save(update_fields=['description'])
            changed += 1
        rows = list(course.modules.order_by('order', 'id'))
        for mi, module in enumerate(modules):
            row = rows[mi] if mi < len(rows) else None
            if row is None:
                row = CourseModule.objects.create(course=course, title=module['title'], order=mi)
                rows.append(row)
                changed += 1
            elif row.title != module['title']:
                row.title = module['title']
                row.save(update_fields=['title'])
                changed += 1
            lessons = list(row.lessons.order_by('order', 'id'))
            for li, lesson in enumerate(module['lessons']):
                item = lessons[li] if li < len(lessons) else None
                if item is None:
                    item = CourseLesson.objects.create(
                        course=course, module=row, order=li, title=lesson['title'],
                        is_required=lesson.get('required', True), mark_required=lesson.get('mark', True))
                    lessons.append(item)
                    changed += 1
                elif item.title != lesson['title']:
                    item.title = lesson['title']
                    item.save(update_fields=['title'])
                    changed += 1
                changed += self.refresh_blocks(item, lesson['blocks'], lang)
        return changed

    def refresh_blocks(self, lesson, specs, lang):
        changed = 0
        blocks = list(lesson.blocks.order_by('order', 'id'))
        for bi, spec in enumerate(specs):
            block = blocks[bi] if bi < len(blocks) else None
            if block is None:
                self.add_block(lesson, bi, spec, lang)
                changed += 1
                continue
            if block.type != spec['type']:
                continue  # a teacher put another kind of block here: leave it
            fields = self.block_fields(spec, lang)
            keep = {'text': fields['text'], 'title': fields['title']}
            if block.type == 'video':
                keep['youtube_id'] = fields['youtube_id']
            if block.type == 'problem':
                keep.pop('title')
            if any(getattr(block, k) != v for k, v in keep.items()):
                for k, v in keep.items():
                    setattr(block, k, v)
                block.save()
                changed += 1
            if block.type == 'test':
                changed += self.refresh_questions(block, spec['questions'], lang)
        return changed

    def refresh_questions(self, block, specs, lang):
        changed = 0
        questions = list(block.questions.order_by('order', 'id'))
        for qi, q in enumerate(specs):
            question = questions[qi] if qi < len(questions) else None
            if question is None:
                self.add_question(block, qi, q, lang)
                changed += 1
                continue
            question.type = q.get('type', CourseQuestion.SINGLE)
            question.text = question_text(q, lang)
            question.explanation = q.get('expl', '')
            question.points = q.get('points', 1)
            question.save()
            question.options.all().delete()
            self.add_options(question, q)
            changed += 1
        return changed
