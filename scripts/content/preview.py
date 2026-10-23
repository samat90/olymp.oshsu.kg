"""Seed only public content into the explicitly isolated local preview database."""
import json
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
os.environ['DJANGO_SETTINGS_MODULE']='dmoj.preview_settings'
import django
django.setup()
from django.conf import settings
from django.db import transaction
from django.test import Client
from judge.models import Contest, ContestProblem, Problem, ProblemGroup
from judge.jinja2.markdown import markdown
from lxml import html

assert settings.DATABASES['default']['ENGINE']=='django.db.backends.sqlite3'
assert Path(settings.DATABASES['default']['NAME']).name=='ui-preview.sqlite3'
folder=ROOT/'artifacts/content-audit'
original=json.loads((folder/'original.json').read_text(encoding='utf8'))
release=json.loads((folder/'release.json').read_text(encoding='utf8'))
old={p['code']:p for p in original['problems']}
mapping={}
with transaction.atomic():
    group,_=ProblemGroup.objects.get_or_create(name='archive-preview',defaults={'full_name':'Архив задач'})
    for row in release['problems']:
        source=old[row['code']]
        defaults={key:source[key] for key in ('time_limit','memory_limit','points','partial','is_public','is_manually_managed')}
        defaults.update(name=row['name'],description=row['description'],group=group)
        obj,_=Problem.objects.update_or_create(code=row['code'],defaults=defaults)
        mapping[row['id']]=obj.pk
    for source in original['contests']:
        row=next(c for c in release['contests'] if c['key']==source['key'])
        defaults={k:source[k] for k in ('name','start_time','end_time','time_limit','format_name','format_config','is_visible','is_rated')}
        defaults.update(description=row['description'],summary=row['summary'])
        obj,_=Contest.objects.update_or_create(key=row['key'],defaults=defaults)
        for cp in original['contest_problems']:
            if cp['contest_id']==source['id']:
                ContestProblem.objects.update_or_create(contest=obj,problem_id=mapping[cp['problem_id']],defaults={'order':cp['order'],'points':cp['points'],'partial':cp['partial']})
for row in release['problems']:
    tree=html.fragment_fromstring(str(markdown(row['description'],'problem','jax')),create_parent=True)
    headings=tree.xpath('.//h4/text()')
    assert 'Входные данные' in headings and 'Выходные данные' in headings, row['code']
    blocks=tree.xpath('.//pre/code')
    assert len(blocks)==2*len(row['examples']), (row['code'],len(blocks))
    for i,example in enumerate(row['examples']):
        for j in (0,1):
            assert blocks[2*i+j].text_content().rstrip('\n')==example[j], (row['code'],'rendered example changed')
client=Client()
for code in ('aplusb','nn26-desks','nn26-pik-lenin','sort-007','geo-005','dp-020','math-018'):
    response=client.get('/problem/'+code)
    assert response.status_code==200,(code,response.status_code)
for row in release['contests']:
    for path in ('/contest/'+row['key'], '/contest/'+row['key']+'/ranking/'):
        response=client.get(path)
        assert response.status_code==200,(path,response.status_code)
        if path=='/contest/'+row['key']:
            tree=html.fromstring(response.content)
            scores=tree.xpath('//div[@class="contest-problems"]//tbody/tr/td[2]/text()')
            expected=[cp for cp in original['contest_problems'] if cp['contest_id']==row['id']]
            assert len(scores)==len(expected) and all(s.strip().rstrip('p')=='100' for s in scores),scores
print(f"PASS: all {len(release['problems'])} statements rendered; "
      f"all {sum(len(p['examples']) for p in release['problems'])} example pairs preserved; preview routes returned 200.")
