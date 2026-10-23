"""Complete missing topic labels and classify the six existing contest tasks."""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','dmoj.settings')
import django
django.setup()
from django.db import transaction
from judge.models import Problem, ProblemType
from judge.signals import problem_update

TOPICS = {'nn26-bells':'Математика','nn26-desks':'Математика',
          'nn26-abiturients':'Сортировка','nn26-digitsort':'Сортировка',
          'nn26-trails':'Графы','nn26-pik-lenin':'DP'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup',type=Path)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    with transaction.atomic():
        types={t.name:t for t in ProblemType.objects.select_for_update()}
        problems={p.code:p for p in Problem.objects.select_for_update().filter(code__in=TOPICS)}
        assert set(problems)==set(TOPICS)
        uncategorized={t.pk for t in types.values() if t.name=='uncategorized'}
        before={'types':list(ProblemType.objects.values('id','name','full_name')),
                'problem_types':{code:list(p.types.values_list('id',flat=True)) for code,p in problems.items()}}
        for code,problem in problems.items():
            assert set(before['problem_types'][code]) <= uncategorized, 'Task already has a reviewed topic: '+code
            assert TOPICS[code] in types
        if args.apply:
            if args.backup.exists():
                raise ValueError('Topic backup already exists')
            args.backup.write_text(json.dumps(before,ensure_ascii=False,indent=2),encoding='utf-8')
            for topic in types.values():
                if not topic.full_name:
                    topic.full_name={'DP':'Динамическое программирование','Жадные':'Жадные алгоритмы'}.get(topic.name,topic.name)
                    topic.save(update_fields=['full_name'])
            for code,problem in problems.items():
                problem.types.set([types[TOPICS[code]]])
    if args.apply:
        for problem in problems.values():
            problem_update(Problem,problem)
    print(json.dumps(dict(mode='apply' if args.apply else 'check', classified=len(problems))))


if __name__=='__main__':
    main()
