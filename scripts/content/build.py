"""Build and audit the complete content release from a private production export."""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import yaml

from catalog import CATALOG
import catalog_extra  # noqa: F401; registers the rest of the reviewed catalog
from oracles import identify, solve


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def render(problem):
    family, params = identify(problem)
    params = dict(params)
    if family == 'stairs':
        params['steps_text'] = ', '.join(map(str, params['steps']))
    item = CATALOG[family]
    samples = [tuple(text.format(**params) for text in example) for example in item['examples']]
    if family == 'stairs':
        # Independently enumerate ordered compositions for these small examples.
        def paths(n):
            if n == 0:
                return [()]
            return [(step,) + tail for step in params['steps'] if step <= n for tail in paths(n-step)]
        for n in (3, 4):
            choices = paths(n)
            explanation = ('Последовательности ходов: ' + '; '.join(' + '.join(map(str, x)) for x in choices) + '.') if choices else 'С такими ходами достичь этой ступени невозможно.'
            samples.append((str(n), str(len(choices)), explanation))
    for raw, expected, _ in samples:
        actual = solve(family, params, raw)
        assert actual.split() == expected.split(), (problem['code'], raw, expected, actual)
    name = problem['name']
    if family in {'sum_n', 'sum_squares', 'sum_cubes'}:
        name = {'sum_n':'Сумма чисел', 'sum_squares':'Сумма квадратов', 'sum_cubes':'Сумма кубов'}[family] + ' (N ≤ ' + str(params['limit']) + ')'
    elif family == 'budget':
        name = 'Максимальное количество покупок #' + str((int(problem['code'].split('-')[1])-1)//3+1)
    elif family == 'pascal':
        name = 'Строка треугольника Паскаля #' + str((int(problem['code'].split('-')[1])-1)//5+1)
    parts = [item['body'].format(**params), '## Входные данные', item['input'].format(**params), '## Выходные данные', item['output'].format(**params)]
    # The statement defines the contract; routine examples do not need a walkthrough.
    samples = samples[:1]
    for raw, expected, _ in samples:
        parts.extend(['## Пример', '**Ввод**', '```\n' + raw + '\n```', '**Вывод**', '```\n' + expected + '\n```'])
    description = '\n\n'.join(parts) + '\n'
    assert samples and description.strip()
    assert not re.search(r'\{(?:limit|base|mod|steps)', description)
    return dict(id=problem['id'], code=problem['code'], name=name, description=description,
                before=dict(name=problem['name'], description=problem['description']),
                family=family, params=params, examples=samples)


def contests(original, revised):
    by_id = {p['id']:p for p in revised}
    result = []
    schedule = {'nedelya-nauki-2026':'28 апреля 2026 года, с 13:00 до 16:00', 'programmerday':'13 сентября 2026 года, с 12:00 до 15:00'}
    for contest in original['contests']:
        links = sorted((x for x in original['contest_problems'] if x['contest_id']==contest['id']), key=lambda x:x['order'])
        assert contest['format_name']=='default' and all(x['points']==100 and x['partial'] for x in links)
        tasks = '\n'.join(f"{i}. [{by_id[x['problem_id']]['name']}](/problem/{by_id[x['problem_id']]['code']}) — {x['points']} баллов." for i,x in enumerate(links,1))
        description = (
            f"Контест «{contest['name']}» на олимпиадной платформе ОшГУ. Соревнование завершено; условия задач доступны для изучения и самостоятельной практики.\n\n"
            f"## Время проведения\n\n{schedule[contest['key']]} по времени Бишкека (UTC+6). Продолжительность — 3 часа.\n\n"
            f"## Задачи\n\nВ контест входят {len(links)} задач. Порядок ниже соответствует порядку в контесте.\n\n{tasks}\n\n"
            f"## Оценивание\n\nЗа каждую задачу можно получить до 100 баллов; максимальная сумма — {100*len(links)}. Предусмотрены частичные баллы за пройденные тесты согласно настройкам каждой задачи. В зачёт идёт лучший балл по каждой задаче, затем баллы суммируются.\n\n"
            "При равной сумме баллов выше располагается участник с меньшей суммой времён последних посылок по задачам с ненулевым результатом. Время каждой такой посылки отсчитывается от начала участия.\n\n"
            f"## Результаты\n\n[Открыть таблицу результатов](/contest/{contest['key']}/ranking). Решения, отправленные после окончания основного соревнования, не изменяют его итоговую таблицу.\n"
        )
        summary = f"Архив контеста «{contest['name']}»: {len(links)} задач, 3 часа, до {100*len(links)} баллов."
        result.append(dict(id=contest['id'], key=contest['key'], description=description, summary=summary,
                           before={k:contest[k] for k in ('description','summary')}))
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path, default=Path('artifacts/content-audit'))
    args=parser.parse_args(); folder=args.directory
    original=json.loads((folder/'original.json').read_text(encoding='utf-8-sig'))
    assert not original['translations'], 'Translations require a separate review'
    codes={p['code'] for p in original['problems']}
    test_root=folder/'judge-data/problems'
    assert codes=={p.name for p in test_root.iterdir() if p.is_dir()}
    revised=[]; rows=[]; count=0
    for problem in original['problems']:
        updated=render(problem); revised.append(updated)
        config=yaml.safe_load((test_root/problem['code']/'init.yml').read_text(encoding='utf-8'))
        assert config.get('checker','standard')=='standard'
        cases=config['test_cases']
        for case in cases:
            assert 'batched' not in case, 'Review batch separately'
            raw=(test_root/problem['code']/case['in']).read_text(encoding='utf-8')
            expected=(test_root/problem['code']/case['out']).read_text(encoding='utf-8')
            actual=solve(updated['family'], updated['params'], raw)
            assert actual.split()==expected.split(), (problem['code'],case['in'],actual,expected)
            count+=1
        rows.append(dict(code=problem['code'],family=updated['family'],tests=len(cases),examples=len(updated['examples']),old_chars=len(problem['description']),new_chars=len(updated['description']),status='PASS'))
    release=dict(schema=1, original_sha256=digest(original), problems=revised, contests=contests(original,revised))
    (folder/'release.json').write_text(json.dumps(release,ensure_ascii=False,indent=2),encoding='utf-8')
    with (folder/'review.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    report=dict(problems=len(revised),contests=len(release['contests']),test_cases=count,
                examples=sum(len(p['examples']) for p in revised),families=dict(Counter(p['family'] for p in revised)),
                changed_names=sum(p['name']!=p['before']['name'] for p in revised),release_sha256=digest(release))
    (folder/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='families'}))


if __name__=='__main__':
    main()
