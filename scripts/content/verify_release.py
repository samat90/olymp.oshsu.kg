"""Verify content and unchanged exported settings after publication."""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','dmoj.settings')
import django
django.setup()
from django.test import Client
from judge.models import Contest, ContestProblem, Problem, ProblemTranslation
from lxml import html

parser=argparse.ArgumentParser()
parser.add_argument('directory',type=Path)
args=parser.parse_args()
original=json.loads((args.directory/'original.json').read_text(encoding='utf8'))
release=json.loads((args.directory/'release.json').read_text(encoding='utf8'))
assert Problem.objects.count()==len(original['problems'])
assert Contest.objects.count()==len(original['contests'])
assert not ProblemTranslation.objects.exists()
for model,kind,key,changed in [(Problem,'problems','code',('name','description')),(Contest,'contests','key',('description','summary'))]:
    new={p[key]:p for p in release[kind]}
    for before in original[kind]:
        actual=model.objects.values(*before.keys()).get(**{key:before[key]})
        actual=json.loads(json.dumps(actual,default=str))
        expected=dict(before)
        expected.update({field:new[before[key]][field] for field in changed})
        assert actual==expected, (kind,before[key],'content or protected settings mismatch')
actual=list(ContestProblem.objects.values().order_by('id'))
assert actual==sorted(original['contest_problems'],key=lambda x:x['id'])
client=Client(HTTP_HOST='olymp.oshsu.kg')
for row in release['problems']:
    response=client.get('/problem/'+row['code'],secure=True)
    assert response.status_code==200,(row['code'],response.status_code)
    text=response.content.decode()
    assert 'Входные данные' in text and 'Выходные данные' in text and 'Пример' in text,row['code']
for row in release['contests']:
    for path in ('/contest/'+row['key'],'/contest/'+row['key']+'/ranking/'):
        response=client.get(path,secure=True)
        assert response.status_code==200,(path,response.status_code)
        if path=='/contest/'+row['key']:
            tree=html.fromstring(response.content)
            scores=tree.xpath('//div[@class="contest-problems"]//tbody/tr/td[2]/text()')
            expected=[cp for cp in original['contest_problems'] if cp['contest_id']==row['id']]
            assert len(scores)==len(expected) and all(s.strip().rstrip('p')=='100' for s in scores),scores
print(json.dumps(dict(problems=len(release['problems']),contests=len(release['contests']),http_pages=1039,protected_settings='unchanged',status='PASS')))
