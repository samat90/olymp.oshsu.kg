#!/usr/bin/env python3
"""Build tests for the pure-Python problem set (works on any machine with Python 3, also on the server).

Every module in problems/ defines PROBLEMS: a list of dicts built with P(...) (see lib.py).
For each problem the builder
  1. checks the reference solution against the brute force on the samples and on many random small inputs,
  2. generates 10 tests of growing size (100 points, 10 per test) and their answers,
  3. writes build/<slug>/{manifest.json, statement.md, tests/NN.in|out} for `manage.py import_problemset`.

    python3 build.py [slug ...] [--out DIR] [--no-stress] [--no-brute] [--names]

Output goes to build/ next to this file by default. --names rewrites names.txt (slug<TAB>problem name),
which scripts/server/import_problemsets.sh reads to see what is missing on the site.
"""
import hashlib
import importlib
import json
import os
import pkgutil
import random
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
STRESS = 300
NL, TAB = chr(10), chr(9)


def load():
    import problems
    import lib
    found = {}
    mods = [importlib.import_module('problems.' + m.name) for m in pkgutil.iter_modules(problems.__path__)]
    for p in [p for m in mods for p in getattr(m, 'PROBLEMS', [])] + lib.REG:
        if True:
            if p['slug'] in found:
                raise SystemExit('duplicate slug ' + p['slug'])
            found[p['slug']] = p
    return found


def same(a, b):
    return a.split() == b.split()


def build(p, out, stress=True, check=True):
    slug = p['slug']
    solve, brute, gen = p['solve'], p['brute'], p['gen']
    for s in p['samples']:
        a, b = solve(s), brute(s)
        if not same(a, b):
            raise RuntimeError('%s: brute disagrees on a sample\n%s\n%r vs %r' % (slug, s, a, b))
    for i in range(STRESS):
        data = gen(random.Random(slug + str(i)), i % 3)
        a, b = solve(data), brute(data)
        if not same(a, b):
            raise RuntimeError('%s: stress %d disagrees\n%s\nsolve=%r\nbrute=%r' % (slug, i, data, a, b))
    folder = os.path.join(out, slug)
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(os.path.join(folder, 'tests'))
    cases, seen, number = [], set(), 0

    def add(data, group):
        nonlocal number
        number += 1
        name = '%02d' % number
        ans = solve(data)
        open(os.path.join(folder, 'tests', name + '.in'), 'w', encoding='utf-8', newline='\n').write(data)
        open(os.path.join(folder, 'tests', name + '.out'), 'w', encoding='utf-8', newline='\n').write(ans)
        cases.append({'group': group, 'in': name + '.in', 'out': name + '.out', 'size': len(data) + len(ans)})
        return ans

    texts = []
    for s in p['samples']:
        texts.append((s, add(s, 0)))
    for level in range(10):
        for attempt in range(40):
            data = p['gen'](random.Random('%s/%d/%d' % (slug, level, attempt)), level)
            h = hashlib.sha1(data.encode()).hexdigest()
            if h not in seen:
                break
        else:
            raise RuntimeError('%s: cannot make distinct test %d' % (slug, level))
        seen.add(h)
        if level < 3 and check:
            if not same(solve(data), brute(data)):
                raise RuntimeError('%s: brute disagrees on test %d' % (slug, level))
        add(data, 1)

    ex = ''
    for i, (a, b) in enumerate(texts, 1):
        ex += '\n## Пример %d\n\nВход:\n```\n%s```\n\nВыход:\n```\n%s```\n' % (i, a, b if b.endswith('\n') else b + '\n')
    statement = p['text'].replace('{{samples}}', ex)
    open(os.path.join(folder, 'statement.md'), 'w', encoding='utf-8').write(statement)
    manifest = {'name': p['name'], 'time': p['time'], 'memory': 256, 'difficulty': p['diff'], 'points': 100,
                'types': p['types'], 'group': p['group'],
                'groups': [{'points': 0, 'batch': True}, {'points': 10, 'batch': False}],
                'cases': cases, 'images': []}
    json.dump(manifest, open(os.path.join(folder, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('ok  %-24s %s' % (slug, p['name']), flush=True)


def main():
    args = sys.argv[1:]
    out = os.path.join(ROOT, 'build')
    if '--out' in args:
        k = args.index('--out'); out = args[k + 1]; del args[k:k + 2]
    flags = {a for a in args if a.startswith('--')}
    only = [a for a in args if not a.startswith('--')]
    probs = load()
    names_seen = {}
    for n, p in probs.items():
        if only and n not in only:
            continue
        if p['name'] in names_seen:
            raise SystemExit('duplicate name %r' % p['name'])
        names_seen[p['name']] = n
    if '--names' in flags:
        with open(os.path.join(ROOT, 'names.txt'), 'w', encoding='utf-8', newline=NL) as f:
            for n, p in sorted(probs.items()):
                f.write('%s%s%s%s' % (n, TAB, p['name'], NL))
        return
    failed = []
    for n in [n for n in probs if not only or n in only]:
        try:
            build(probs[n], out, '--no-stress' not in flags, '--no-brute' not in flags)
        except Exception as e:
            print('FAILED', n, e, flush=True)
            failed.append(n)
    if failed:
        sys.exit('failed: ' + ' '.join(failed))


if __name__ == '__main__':
    main()
