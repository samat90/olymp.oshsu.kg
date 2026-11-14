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
from statement_math import clean_math
import math
import time
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
    # A problem whose name repeats an earlier one is dropped (hand-written ones come first, then batch folders).
    taken = set()
    for k in sorted(found, key=lambda k: (k.startswith('batch'), k)) if False else sorted(found, key=lambda k: k.startswith('batch')):
        if found[k]['name'] in taken:
            print('skipped %s: name %r already used' % (k, found[k]['name']), flush=True)
            del found[k]
        else:
            taken.add(found[k]['name'])
    return found


def same(a, b):
    return a.split() == b.split()


def build_simple(p, out, check=True):
    """Folder format: programs run as black boxes. Tests: gen.py K for ten consecutive K; brute on small ones."""
    import subprocess
    folder = p['simple']; slug = p['slug']
    def run(script, data, *args):
        res = subprocess.run([sys.executable, os.path.join(folder, script)] + list(args), input=data, capture_output=True, timeout=300)
        if res.returncode:
            raise RuntimeError('%s %s failed: %s' % (slug, script, res.stderr.decode()[-500:]))
        return res.stdout
    dest = os.path.join(out, slug)
    shutil.rmtree(dest, ignore_errors=True)
    os.makedirs(os.path.join(dest, 'tests'))
    cases, seen, worst = [], set(), 0.0
    for i in range(10):
        m = p['meta']
        if 'test_levels' in m:
            data = run('gen.py', b'', str(m['seed_base'] + i + 1), str(m['test_levels'][i]))
        else:
            data = run('gen.py', b'', str(p['first_k'] + i))
        t0 = time.time()
        ans = run('sol.py', data)
        worst = max(worst, time.time() - t0)
        if check and len(data) <= 3000:
            try:  # exponential brute forces are simply skipped (the authors stress-checked them)
                other = subprocess.run([sys.executable, os.path.join(folder, 'brute.py')], input=data, capture_output=True, timeout=10)
            except subprocess.TimeoutExpired:
                other = None
            if other is not None and other.returncode == 0 and not same(ans.decode(), other.stdout.decode()):
                raise RuntimeError('%s: brute disagrees on test %d' % (slug, i))
        name = '%02d' % (i + 1)
        cr = bytes([13])
        open(os.path.join(dest, 'tests', name + '.in'), 'wb').write(data.replace(cr, b''))
        open(os.path.join(dest, 'tests', name + '.out'), 'wb').write(ans.replace(cr, b''))
        cases.append({'group': 0, 'in': name + '.in', 'out': name + '.out', 'size': len(data) + len(ans)})
    open(os.path.join(dest, 'statement.md'), 'w', encoding='utf-8', newline=NL).write(
        clean_math(open(os.path.join(folder, 'statement.md'), encoding='utf-8').read()))
    tl = p['time']
    if worst > 0.6 * tl:  # the Python reference is much slower than compiled solutions; leave it room
        tl = min(6, math.ceil(worst * 1.5))
    manifest = {'name': p['name'], 'time': tl, 'memory': 256, 'difficulty': p['diff'], 'points': 100,
                'types': p['types'], 'group': p['group'], 'groups': [{'points': 10, 'batch': False}],
                'cases': cases, 'images': []}
    json.dump(manifest, open(os.path.join(dest, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('ok  %-24s %s%s' % (slug, p['name'], '' if worst < p['time'] * 0.6 else '  SLOW %.2fs (TL %s)' % (worst, p['time'])), flush=True)


def build(p, out, stress=True, check=True):
    if p.get('simple'):
        return build_simple(p, out, check)
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
    statement = clean_math(p['text'].replace('{{samples}}', ex))
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
