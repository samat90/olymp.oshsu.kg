"""Problems delivered as folders batchNN/<code>/ with statement.md, gen.py (`python3 gen.py K`), sol.py, brute.py, meta.json.

They are built by build.build_simple(): the programs are run as black boxes (stdin -> stdout), the samples are the
ones written in the statement itself. The authors checked sol.py against brute.py before delivery; the builder
re-checks the small tests.
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBLEMS = []
ALLOWED = {'Реализация', 'Математика', 'Теория чисел', 'Комбинаторика', 'Геометрия', 'Строки', 'Массивы', 'Сортировка',
           'Двоичный поиск', 'Жадные', 'DP', 'Графы', 'Структуры данных', 'Теория игр'}
MAP = {'Динамическое программирование': 'DP', 'Деревья': 'Графы', 'Структуры': 'Структуры данных', 'Жадные алгоритмы': 'Жадные',
       'Игры': 'Теория игр', 'Графы и деревья': 'Графы', 'Теория чисел': 'Теория чисел'}
FIRST_K = {'batch08': 0}  # gen.py argument of the first test; the other batches start at 1


def types_of(meta):
    for key in ('topic_key', 'topic'):
        v = meta.get(key)
        if v in ALLOWED:
            return [v]
        if v in MAP:
            return [MAP[v]]
    return ['Реализация']


for meta_path in sorted(glob.glob(os.path.join(ROOT, 'batch[0-9][0-9]', '*', 'meta.json'))):
    folder = os.path.dirname(meta_path)
    batch = os.path.basename(os.path.dirname(folder))
    meta = json.load(open(meta_path, encoding='utf-8'))
    PROBLEMS.append(dict(
        slug='%s_%s' % (batch, os.path.basename(folder)), name=meta.get('title') or meta['name'],
        group=meta.get('group', 'training'), types=types_of(meta), diff=meta.get('difficulty', 40),
        time=meta.get('time_limit', 1), simple=folder, meta=meta, first_k=FIRST_K.get(batch, 1)))
