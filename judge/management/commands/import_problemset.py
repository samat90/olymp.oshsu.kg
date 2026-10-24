"""Add the problems built by problemsets/<set>/build.py to the site.

Only adds: a problem whose name already exists is skipped and never changed, nothing is deleted.
New problems get the next free six-digit numbers when DMOJ_NUMERIC_PROBLEM_CODES is on.

    python manage.py import_problemset problemsets/kg2026/build --public --dry-run
"""
import io
import json
import os
import shutil
import uuid
import zipfile

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from judge.models import (Problem, ProblemCodeAlias, ProblemData, ProblemGroup, ProblemTestCase, ProblemType,
                          Profile)
from judge.utils.languages import problem_languages
from judge.utils.problem_data import ProblemDataCompiler

GROUP_NAME = 'kyrgyzstan'
GROUP_FULL_NAME = 'Задачи о Кыргызстане'
IMAGE_DIR = os.path.join('problems', 'kg2026')  # inside MEDIA_ROOT; statements link to /media/problems/kg2026/


class Command(BaseCommand):
    help = 'add the problems of a built problem set (never changes or deletes existing problems)'

    def add_arguments(self, parser):
        parser.add_argument('build_dir',
                            help='folder with one sub-folder per problem (manifest.json, statement.md, tests/)')
        parser.add_argument('--public', action='store_true', help='show the new problems in the public list')
        parser.add_argument('--author', help='username to list as the author')
        parser.add_argument('--only', nargs='*', help='import only these sub-folders')
        parser.add_argument('--dry-run', action='store_true', help='only report what would be added')

    def handle(self, *args, **options):
        root = options['build_dir']
        if not os.path.isdir(root):
            raise CommandError('No such folder: %s' % root)
        names = sorted(d for d in os.listdir(root) if os.path.exists(os.path.join(root, d, 'manifest.json')))
        if options['only']:
            names = [n for n in names if n in options['only']]
        author = Profile.objects.get(user__username=options['author']) if options['author'] else None

        todo = [f for f in names if not Problem.objects.filter(
            name=json.load(open(os.path.join(root, f, 'manifest.json'), encoding='utf-8'))['name']).exists()]
        self.check_numbers(len(todo))

        added = skipped = 0
        for folder in names:
            path = os.path.join(root, folder)
            manifest = json.load(open(os.path.join(path, 'manifest.json'), encoding='utf-8'))
            name = manifest['name']
            existing = Problem.objects.filter(name=name).first()
            if existing:
                self.stdout.write('skip  %-12s "%s" already exists as %s' % (folder, name, existing.code))
                skipped += 1
                continue
            if options['dry_run']:
                self.stdout.write('would add %-12s "%s" (%d tests)' % (folder, name, len(manifest['cases'])))
                continue
            problem = self.add_problem(folder, path, manifest, options['public'], author)
            self.stdout.write('added %-12s "%s" as %s' % (folder, name, problem.code))
            added += 1
        self.stdout.write('Done: %d added, %d skipped.' % (added, skipped))

    def check_numbers(self, count):
        """Show the six-digit numbers the new problems will get and stop if any of them is taken."""
        if not count or not getattr(settings, 'DMOJ_NUMERIC_PROBLEM_CODES', False):
            return
        table = Problem._meta.db_table
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute("SELECT pg_get_serial_sequence(%s, 'id')", [table])
                seq = cursor.fetchone()[0]
                cursor.execute('SELECT last_value, is_called FROM %s' % seq)
                last, called = cursor.fetchone()
                first = last + 1 if called else last
            else:
                first = (Problem.objects.order_by('-id').values_list('id', flat=True).first() or 0) + 1
        first = max(first, (Problem.objects.order_by('-id').values_list('id', flat=True).first() or 0) + 1)
        codes = ['%06d' % i for i in range(first, first + count)]
        taken = sorted(set(Problem.objects.filter(code__in=codes).values_list('code', flat=True)) |
                       set(ProblemCodeAlias.objects.filter(code__in=codes).values_list('code', flat=True)))
        self.stdout.write('New problems will get numbers %s ... %s' % (codes[0], codes[-1]))
        if taken:
            raise CommandError('These numbers are already used: %s. Nothing was added.' % ', '.join(taken))

    def add_problem(self, folder, path, manifest, public, author):
        statement = open(os.path.join(path, 'statement.md'), encoding='utf-8').read()
        self.copy_images(path, manifest.get('images', []))

        tests = io.BytesIO()
        with zipfile.ZipFile(tests, 'w', zipfile.ZIP_DEFLATED) as zf:
            for case in manifest['cases']:
                zf.write(os.path.join(path, 'tests', case['in']), case['in'])
                zf.write(os.path.join(path, 'tests', case['out']), case['out'])

        numeric = getattr(settings, 'DMOJ_NUMERIC_PROBLEM_CODES', False)
        with transaction.atomic():
            group, _ = ProblemGroup.objects.get_or_create(name=GROUP_NAME, defaults={'full_name': GROUP_FULL_NAME})
            problem = Problem(
                code=('imp' + uuid.uuid4().hex[:12]) if numeric else ('kg' + folder)[:20],
                name=manifest['name'],
                description=statement,
                time_limit=manifest['time'],
                memory_limit=manifest['memory'] * 1024,
                points=manifest.get('points', 100),
                partial=True,
                is_public=public,
                difficulty=manifest.get('difficulty'),
                group=group,
            )
            problem.save()
            problem.allowed_languages.set(problem_languages())
            types = []
            for type_name in manifest.get('types', []):
                ptype, _ = ProblemType.objects.get_or_create(name=type_name, defaults={'full_name': type_name})
                types.append(ptype)
            problem.types.set(types)
            if author is not None:
                problem.authors.add(author)

            data = ProblemData.objects.create(problem=problem)
            data.zipfile.save('tests.zip', ContentFile(tests.getvalue()), save=True)
            rows, order = [], 0
            by_group = {}
            for case in manifest['cases']:
                by_group.setdefault(case['group'], []).append(case)
            for gi, group_info in enumerate(manifest['groups']):
                cases = by_group.get(gi, [])
                if not cases:
                    continue
                batch = group_info.get('batch', True) or group_info.get('points', 0) == 0
                if batch:
                    order += 1
                    rows.append(ProblemTestCase(dataset=problem, order=order, type='S',
                                                points=group_info['points'], is_pretest=False))
                for case in cases:
                    order += 1
                    rows.append(ProblemTestCase(dataset=problem, order=order, type='C', input_file=case['in'],
                                                output_file=case['out'], is_pretest=False,
                                                points=None if batch else group_info['points']))
                if batch:
                    order += 1
                    rows.append(ProblemTestCase(dataset=problem, order=order, type='E', is_pretest=False))
            ProblemTestCase.objects.bulk_create(rows)

        files = [n for c in manifest['cases'] for n in (c['in'], c['out'])]
        ProblemDataCompiler.generate(problem, data, problem.cases.order_by('order'), files)
        data.refresh_from_db()
        if data.feedback:
            self.stdout.write(self.style.WARNING('  %s: %s' % (problem.code, data.feedback)))
        return problem

    def copy_images(self, path, images):
        if not images:
            return
        target = os.path.join(settings.MEDIA_ROOT, IMAGE_DIR)
        os.makedirs(target, exist_ok=True)
        for image in images:
            dest = os.path.join(target, image)
            if os.path.exists(dest):
                continue  # never overwrite files that are already there
            shutil.copy(os.path.join(path, image), dest)
