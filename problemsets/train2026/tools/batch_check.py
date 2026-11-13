#!/usr/bin/env python3
"""Check/build one batch only: python tools/batch_check.py b02 [slug ...] [--no-stress]
Imports only problems/<prefix>_*.py (other batches' half-written files cannot break it),
checks slug/name uniqueness against ALL problem files (by regex), runs build() into build_<prefix>/."""
import importlib, os, pkgutil, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import build as B, lib
pre = sys.argv[1]
args = [a for a in sys.argv[2:] if not a.startswith('--')]
import problems
mods = [importlib.import_module('problems.' + m.name) for m in pkgutil.iter_modules(problems.__path__) if m.name.startswith(pre + '_')]
probs = {}
for p in [p for m in mods for p in getattr(m, 'PROBLEMS', [])] + [p for p in lib.REG if p['slug'].startswith(pre + '_')]:
    assert p['slug'].startswith(pre + '_'), 'slug must start with ' + pre + '_: ' + p['slug']
    assert p['slug'] not in probs, 'dup slug ' + p['slug']
    probs[p['slug']] = p
# global uniqueness of names vs other files
others = {}
for f in os.listdir(os.path.join(ROOT, 'problems')):
    if f.endswith('.py') and not f.startswith(pre + '_'):
        t = open(os.path.join(ROOT, 'problems', f), encoding='utf-8').read()
        for m in re.finditer(r"^# (.+)$", t, re.M):
            others[m.group(1).strip()] = f
for line in open(os.path.join(ROOT, 'names.txt'), encoding='utf-8'):
    others[line.rstrip('\n').split('\t')[-1]] = 'names.txt'
seen = {}
for s, p in probs.items():
    assert p['name'] not in seen, 'dup name ' + p['name']
    seen[p['name']] = s
    if p['name'] in others: print('NAME CLASH', p['name'], others[p['name']])
print(len(probs), 'problems in batch', pre)
out = os.path.join(ROOT, 'build_' + pre)
bad = []
for s, p in probs.items():
    if args and s not in args: continue
    try:
        B.build(p, out, '--no-stress' not in sys.argv)
    except Exception as e:
        print('FAILED', s, str(e)[:500]); bad.append(s)
print('failed:', bad)
