#!/usr/bin/env python3
"""Build tests for the problems in this folder and check the solutions against each other.

Every problem lives in its own folder with:
    problem.json   name, limits, difficulty, tests (see README.md)
    statement.md   the statement; {{sample N}} is replaced by sample N from samples/
    sol.cpp        reference solution (produces the answers)
    alt.cpp/.py    optional second solution, must agree on every test
    brute.cpp/.py  optional slow solution, must agree on tests marked "brute"
    gen.py         test generator: python3 gen.py <args...> prints one test
    samples/N.in   samples shown in the statement

Usage (inside WSL or Linux):  python3 build.py [problem ...] [--no-alt]
Output goes to build/<problem>/: tests/NN.in|out, statement.md, manifest.json.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, 'build')
BIN = os.path.join(BUILD, '.bin')
IMAGE_URL = '/media/problems/kg2026'  # the import command copies img/ files to MEDIA_ROOT/problems/kg2026
CXX = ['g++', '-O2', '-w', '-std=gnu++17', '-pipe']


def log(*args):
    print(*args, flush=True)


def compile_cpp(path):
    os.makedirs(BIN, exist_ok=True)
    digest = hashlib.sha1(open(path, 'rb').read()).hexdigest()[:12]
    exe = os.path.join(BIN, '%s-%s' % (os.path.basename(os.path.dirname(path)) + '_' +
                                         os.path.splitext(os.path.basename(path))[0], digest))
    if not os.path.exists(exe):
        subprocess.run(CXX + ['-o', exe, path], check=True)
    return [exe]


def program(folder, stem):
    for ext in ('.cpp', '.py'):
        path = os.path.join(folder, stem + ext)
        if os.path.exists(path):
            return compile_cpp(path) if ext == '.cpp' else [sys.executable, path]
    return None


def run(cmd, data, timeout=120):
    start = time.time()
    res = subprocess.run(cmd, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if res.returncode != 0:
        raise RuntimeError('%s failed (%d): %s' % (' '.join(cmd), res.returncode, res.stderr.decode()[-2000:]))
    return res.stdout, time.time() - start


def tokens(data):
    return data.split()


def build(name, no_alt=False):
    folder = os.path.join(ROOT, name)
    meta = json.load(open(os.path.join(folder, 'problem.json'), encoding='utf-8'))
    out = os.path.join(BUILD, name)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.join(out, 'tests'), exist_ok=True)

    sol = program(folder, 'sol')
    alt = None if no_alt else program(folder, 'alt')
    brute = program(folder, 'brute')
    gen = [sys.executable, os.path.join(folder, 'gen.py')]
    samples_dir = os.path.join(folder, 'samples')
    sample_files = sorted((f for f in os.listdir(samples_dir) if f.endswith('.in')),
                          key=lambda f: int(f[:-3])) if os.path.isdir(samples_dir) else []

    # Groups: either "subtasks" (batches with points) or a flat "tests" list (points per test).
    groups = []
    if sample_files:
        groups.append({'points': 0, 'brute': True, 'sample': True,
                       'tests': [['sample', f[:-3]] for f in sample_files]})
    if 'subtasks' in meta:
        for st in meta['subtasks']:
            groups.append({'points': st['points'], 'brute': st.get('brute', False), 'noalt': st.get('noalt', False), 'tests': st['tests'],
                           'batch': True, 'depends': st.get('depends', [])})
    else:
        groups.append({'points': meta.get('test_points', 1), 'brute': False, 'tests': meta['tests'],
                       'batch': False})

    cases, number, worst = [], 0, 0.0
    sample_out = {}
    seen = set()
    for gi, group in enumerate(groups):
        for spec in group['tests']:
            number += 1
            if spec[0] == 'sample':
                data = open(os.path.join(samples_dir, spec[1] + '.in'), 'rb').read()
            else:
                data, _ = run(gen + [str(a) for a in spec], b'')
            digest = hashlib.sha1(data).hexdigest()
            if digest in seen and spec[0] != 'sample':
                raise RuntimeError('%s: test %d duplicates an earlier test (%s)' % (name, number, spec))
            seen.add(digest)
            if 'validate' in meta:
                run(program(folder, 'validate'), data)
            answer, spent = run(sol, data)
            worst = max(worst, spent)
            if alt and not group.get('noalt'):
                other, _ = run(alt, data)
                if tokens(other) != tokens(answer):
                    raise RuntimeError('%s: alt disagrees on test %d (%s)' % (name, number, spec))
            if brute and (group['brute'] or spec[0] == 'sample') and len(data) < 200000:
                other, _ = run(brute, data, timeout=600)
                if tokens(other) != tokens(answer):
                    raise RuntimeError('%s: brute disagrees on test %d (%s)' % (name, number, spec))
            fname = '%02d' % number
            open(os.path.join(out, 'tests', fname + '.in'), 'wb').write(data)
            open(os.path.join(out, 'tests', fname + '.out'), 'wb').write(answer)
            if spec[0] == 'sample':
                sample_out[spec[1]] = (data.decode(), answer.decode())
            cases.append({'group': gi, 'in': fname + '.in', 'out': fname + '.out',
                          'size': len(data) + len(answer)})
        log('  %s: group %d done (%d tests so far, slowest %.2fs)' % (name, gi, number, worst))

    statement = open(os.path.join(folder, 'statement.md'), encoding='utf-8').read()

    def sample(match):
        inp, ans = sample_out[match.group(1)]
        return ('## Пример %s\n\nВход:\n```\n%s```\n\nВыход:\n```\n%s```' %
                (match.group(1), inp if inp.endswith('\n') else inp + '\n',
                 ans if ans.endswith('\n') else ans + '\n'))
    statement = re.sub(r'\{\{sample (\d+)\}\}', sample, statement)
    statement = re.sub(r'\{\{img (\S+?)(?: (\d+))?\}\}', lambda m: '<p style="text-align:center"><img src="%s/%s" '
                       'alt="Рисунок" style="max-width:100%%;width:%spx"></p>' %
                       (IMAGE_URL, m.group(1), m.group(2) or '640'), statement)
    # {{photo file.jpg Caption and credit}}: a photograph with its attribution line
    statement = re.sub(r'\{\{photo (\S+) (.+?)\}\}', lambda m: '<p style="text-align:center"><img src="%s/%s" '
                       'alt="Фотография" style="max-width:100%%;width:560px;border-radius:6px"><br>'
                       '<small style="color:#666">%s</small></p>' % (IMAGE_URL, m.group(1), m.group(2)), statement)
    missing = re.findall(r'\{\{[^}]*\}\}', statement)
    if missing:
        raise RuntimeError('%s: unknown placeholders %s' % (name, missing))
    open(os.path.join(out, 'statement.md'), 'w', encoding='utf-8').write(statement)

    images = []
    img_dir = os.path.join(folder, 'img')
    if os.path.isdir(img_dir):
        for f in sorted(os.listdir(img_dir)):
            shutil.copy(os.path.join(img_dir, f), os.path.join(out, f))
            images.append(f)

    manifest = {k: meta[k] for k in ('name', 'time', 'memory', 'difficulty', 'points', 'types', 'slug')
                if k in meta}
    manifest['groups'] = [{k: g[k] for k in ('points', 'batch', 'depends') if k in g} for g in groups]
    manifest['cases'] = cases
    manifest['images'] = images
    manifest['slowest'] = round(worst, 3)
    if 'checker' in meta:
        manifest['checker'] = meta['checker']
    json.dump(manifest, open(os.path.join(out, 'manifest.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    total = sum(c['size'] for c in cases)
    log('%s: %d tests, %.1f MB, slowest reference run %.2fs (limit %ss)' %
        (name, len(cases), total / 1e6, worst, meta['time']))
    if worst > meta['time'] * 0.6:
        log('  WARNING: reference solution is close to the time limit')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    names = args or sorted(d for d in os.listdir(ROOT)
                           if os.path.exists(os.path.join(ROOT, d, 'problem.json')))
    for name in names:
        build(name, no_alt='--no-alt' in sys.argv)


if __name__ == '__main__':
    main()
