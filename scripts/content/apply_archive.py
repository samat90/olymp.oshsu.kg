"""Atomically apply/roll back reviewed archive content without deleting problem history."""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from judge.models import Problem, ProblemTranslation
from judge.signals import problem_update

FIELDS = ('name', 'description', 'difficulty', 'is_listed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('release', type=Path)
    parser.add_argument('--mode', choices=['check', 'apply', 'rollback'], default='check')
    args = parser.parse_args()
    release = json.loads(args.release.read_text(encoding='utf-8'))
    if release['schema'] != 2:
        raise ValueError('Unsupported archive release')
    with transaction.atomic():
        objects = {p.code:p for p in Problem.objects.select_for_update().all()}
        if set(objects) != {row['code'] for row in release['problems']}:
            raise ValueError('Problem inventory changed')
        if ProblemTranslation.objects.exists():
            raise ValueError('Translations require a separate review')
        for row in release['problems']:
            problem = objects[row['code']]
            if problem.pk != row['id']:
                raise ValueError('Problem identity changed: ' + row['code'])
            for field, expected in row['protected'].items():
                if getattr(problem, field) != expected:
                    raise ValueError('Protected setting changed: ' + row['code'] + '/' + field)
            before, after = (row['after'],row['before']) if args.mode == 'rollback' else (row['before'],row['after'])
            for field in FIELDS:
                if getattr(problem,field) != before[field]:
                    raise ValueError('Content changed: ' + row['code'] + '/' + field)
                setattr(problem,field,after[field])
        if args.mode != 'check':
            Problem.objects.bulk_update(list(objects.values()), FIELDS, batch_size=100)
    if args.mode != 'check':
        for problem in objects.values():
            problem_update(Problem, problem)
        cache.delete('hot_problems:86400:%d' % settings.DMOJ_PROBLEM_HOT_PROBLEM_COUNT)
    print(json.dumps(dict(mode=args.mode, reviewed=len(objects), listed=release['listed'], hidden=release['hidden'])))


if __name__ == '__main__':
    main()
