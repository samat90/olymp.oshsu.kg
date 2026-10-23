"""Guarded, atomic content-only deployment; run with the site's Python environment."""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()
from django.db import transaction
from judge.models import Contest, Problem
from judge.signals import contest_update, problem_update


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('release', type=Path)
    parser.add_argument('--mode',choices=['check','apply','rollback'],default='check')
    args=parser.parse_args()
    release=json.loads(args.release.read_text(encoding='utf-8'))
    assert release['schema']==1
    problem_rows=release['problems']; contest_rows=release['contests']
    with transaction.atomic():
        problems={p.code:p for p in Problem.objects.select_for_update().all()}
        contests={c.key:c for c in Contest.objects.select_for_update().all()}
        assert set(problems)=={p['code'] for p in problem_rows}, 'Problem inventory changed'
        assert set(contests)=={c['key'] for c in contest_rows}, 'Contest inventory changed'
        for rows,objects,key,fields in [(problem_rows,problems,'code',('name','description')),(contest_rows,contests,'key',('description','summary'))]:
            for row in rows:
                obj=objects[row[key]]
                assert obj.pk==row['id'], 'Object identity changed: '+row[key]
                before=row if args.mode=='rollback' else row['before']
                after=row['before'] if args.mode=='rollback' else row
                for field in fields:
                    assert getattr(obj,field)==before[field], 'Content changed since export: '+row[key]+'/'+field
                    setattr(obj,field,after[field])
        if args.mode!='check':
            Problem.objects.bulk_update(list(problems.values()),['name','description'],batch_size=100)
            Contest.objects.bulk_update(list(contests.values()),['description','summary'])
    if args.mode!='check':
        # Use the application's existing invalidation, including cached PDFs.
        for obj in problems.values():
            problem_update(Problem,obj)
        for obj in contests.values():
            contest_update(Contest,obj)
    print(json.dumps(dict(mode=args.mode,problems=len(problems),contests=len(contests))))


if __name__=='__main__':
    main()
