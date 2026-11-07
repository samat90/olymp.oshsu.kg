#!/usr/bin/env python3
"""Build tests for the problems in this folder and check the solutions against each other.

Every problem lives in its own folder with:
    problem.json   name, limits, difficulty, topics, tests, stress specs (see README.md)
    statement.md   the statement; {{sample N}}, {{img file width}} are replaced by the builder
    sol.cpp        reference solution (produces the answers)
    brute.py/.cpp  slow solution: checks the samples, small tests and the random stress runs
    gen.py         test generator: python3 gen.py <args...> prints one test (the last argument is the seed)
    samples/N.in   samples shown in the statement
    img/           pictures for the statement

Usage (inside WSL or Linux):  python3 build.py [problem ...] [--no-stress] [--no-brute]
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


def stress(name, folder, meta, sol, brute, gen):
    """Random small tests: the reference solution must agree with the brute force on every one."""
    total = 0
    for spec in meta.get('stress', []):
        count = meta.get('stress_count', 150)
        for s in range(1, count + 1):
            data, _ = run(gen + [str(a) for a in spec] + [str(100000 + s)], b'')
            answer, _ = run(sol, data)
            other, _ = run(brute, data, timeout=300)
            if tokens(other) != tokens(answer):
                bad = os.path.join(BUILD, name + '-stress-fail.in')
                open(bad, 'wb').write(data)
                raise RuntimeError('%s: brute disagrees on stress %s seed %d (input saved to %s)\nsol: %s\nbrute: %s' %
                                   (name, spec, 100000 + s, bad, answer[:300], other[:300]))
            total += 1
    if total:
        log('  %s: %d stress tests agree' % (name, total))


def build(name, no_stress=False, no_brute=False):
    folder = os.path.join(ROOT, name)
    meta = json.load(open(os.path.join(folder, 'problem.json'), encoding='utf-8'))
    out = os.path.join(BUILD, name)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.join(out, 'tests'), exist_ok=True)

    sol = program(folder, 'sol')
    brute = None if no_brute else program(folder, 'brute')
    gen = [sys.executable, os.path.join(folder, 'gen.py')]
    if brute and not no_stress:
        stress(name, folder, meta, sol, brute, gen)

    samples_dir = os.path.join(folder, 'samples')
    sample_files = sorted((f for f in os.listdir(samples_dir) if f.endswith('.in')),
                          key=lambda f: int(f[:-3])) if os.path.isdir(samples_dir) else []
    tests = meta['tests']
    if 100 % len(tests):
        raise RuntimeError('%s: %d tests do not split 100 points evenly' % (name, len(tests)))
    groups = []
    if sample_files:
        groups.append({'points': 0, 'tests': [['sample', f[:-3]] for f in sample_files]})
    groups.append({'points': 100 // len(tests), 'tests': tests, 'batch': False})
    brute_max = meta.get('brute_max', 3000)

    cases, number, worst, brute_runs = [], 0, 0.0, 0
    sample_out = {}
    seen = set()
    for gi, group in enumerate(groups):
        for spec in group['tests']:
            number += 1
            if spec[0] == 'sample':
                data = open(os.path.join(samples_dir, spec[1] + '.in'), 'rb').read()
            else:
                data, _ = run(gen + [str(a) for a in spec], b'', timeout=900)
            digest = hashlib.sha1(data).hexdigest()
            if digest in seen and spec[0] != 'sample':
                raise RuntimeError('%s: test %d duplicates an earlier test (%s)' % (name, number, spec))
            seen.add(digest)
            answer, spent = run(sol, data)
            worst = max(worst, spent)
            if 'brute_tests' in meta:  # 1-based positions in "tests" where the brute force is fast enough
                small = gi > 0 and group['tests'].index(spec) + 1 in meta['brute_tests']
            else:
                small = len(data) <= brute_max
            if brute and (spec[0] == 'sample' or small):
                other, _ = run(brute, data, timeout=600)
                brute_runs += 1
                if tokens(other) != tokens(answer):
                    raise RuntimeError('%s: brute disagrees on test %d (%s)\nsol: %s\nbrute: %s' %
                                       (name, number, spec, answer[:300], other[:300]))
            fname = '%02d' % number
            open(os.path.join(out, 'tests', fname + '.in'), 'wb').write(data)
            open(os.path.join(out, 'tests', fname + '.out'), 'wb').write(answer)
            if spec[0] == 'sample':
                sample_out[spec[1]] = (data.decode(), answer.decode())
            cases.append({'group': gi, 'in': fname + '.in', 'out': fname + '.out',
                          'size': len(data) + len(answer)})

    statement = open(os.path.join(folder, 'statement.md'), encoding='utf-8').read()

    def sample(match):
        inp, ans = sample_out[match.group(1)]
        return ('## Пример %s\n\nВход:\n```\n%s```\n\nВыход:\n```\n%s```' %
                (match.group(1), inp if inp.endswith('\n') else inp + '\n',
                 ans if ans.endswith('\n') else ans + '\n'))
    statement = re.sub(r'\{\{sample (\d+)\}\}', sample, statement)
    statement = re.sub(r'\{\{img (\S+?)(?: (\d+))?\}\}', lambda m: '<p style="text-align:center"><img src="%s/%s" '
                       'alt="Рисунок" style="max-width:100%%;width:%spx"></p>' %
                       (IMAGE_URL, m.group(1), m.group(2) or '560'), statement)
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
    for f in re.findall(r'\{\{img (\S+?)[ }]', open(os.path.join(folder, 'statement.md'), encoding='utf-8').read()):
        if f not in images:
            raise RuntimeError('%s: picture %s is missing' % (name, f))

    manifest = {k: meta[k] for k in ('name', 'time', 'memory', 'difficulty', 'points', 'types') if k in meta}
    manifest['groups'] = [{k: g[k] for k in ('points', 'batch') if k in g} for g in groups]
    manifest['cases'] = cases
    manifest['images'] = images
    manifest['slowest'] = round(worst, 3)
    json.dump(manifest, open(os.path.join(out, 'manifest.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    total = sum(c['size'] for c in cases)
    log('%s: %d tests, %.1f MB, brute on %d, slowest reference run %.2fs (limit %ss)' %
        (name, len(cases), total / 1e6, brute_runs, worst, meta['time']))
    if worst > meta['time'] * 0.4:
        log('  WARNING: reference solution is close to the time limit')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    names = args or sorted(d for d in os.listdir(ROOT)
                           if os.path.exists(os.path.join(ROOT, d, 'problem.json')))
    failed = []
    for name in names:
        try:
            build(name, no_stress='--no-stress' in sys.argv, no_brute='--no-brute' in sys.argv)
        except Exception as e:  # keep going so that one broken problem does not hide the others
            log('FAILED %s: %s' % (name, e))
            failed.append(name)
    if failed:
        log('Failed: %s' % ' '.join(failed))
        sys.exit(1)


if __name__ == '__main__':
    main()
