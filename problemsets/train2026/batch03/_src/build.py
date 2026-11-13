import sys, os, json, inspect, textwrap, importlib, importlib.util, shutil, random, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reg
BASE = 1329
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'batch03')

def load_all():
    import glob
    for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasks', 't*.py'))):
        name = 'tasks.' + os.path.basename(f)[:-3]
        importlib.import_module(name)

def src(fn):
    return textwrap.dedent(inspect.getsource(fn))

def build(only=None):
    load_all()
    if only is None and os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    for i, t in enumerate(reg.TASKS):
        if only and t['slug'] not in only: continue
        code = BASE + i
        gen, sol, brute = t['fn']()
        d = os.path.join(OUT, t['slug'])
        os.makedirs(d, exist_ok=True)
        open(d + '/gen.py', 'w').write(
            'import random, sys\n\n' + src(gen) + '\n\nSIZES = %r\n\nif __name__ == "__main__":\n    k = int(sys.argv[1])\n    rnd = random.Random(%d * 1000 + k)\n    sys.stdout.write(gen(SIZES[k - 1], rnd, k))\n' % (t['sizes'], code))
        for nm, f in (('sol', sol), ('brute', brute)):
            open(d + '/%s.py' % nm, 'w').write(
                'import sys\n\n' + src(f).replace('def %s(' % f.__name__, 'def %s(' % nm, 1) +
                '\n\nif __name__ == "__main__":\n    sys.stdout.write(%s(sys.stdin.read()) + "\\n")\n' % nm)
        # statement
        samples = t['samples']
        parts = ['# ' + t['title'], '', t['stmt'], '']
        mod = importlib.util.spec_from_file_location('s_' + t['slug'], d + '/sol.py')
        m = importlib.util.module_from_spec(mod); mod.loader.exec_module(m)
        for j, s in enumerate(samples, 1):
            s = s if s.endswith('\n') else s + '\n'
            out = m.sol(s)
            parts += ['## Пример %d' % j if len(samples) > 1 else '## Пример', '', '**Вход**', '```', s.rstrip('\n'), '```', '', '**Выход**', '```', out.rstrip('\n'), '```', '']
        open(d + '/statement.md', 'w').write('\n'.join(parts).rstrip() + '\n')
        json.dump(dict(code='%06d' % code, slug=t['slug'], title=t['title'], topic='Строки', tl=t['tl'],
                       points=100, tests=10, difficulty=t['diff'], seed=code * 1000, sizes=t['sizes']),
                  open(d + '/meta.json', 'w'), ensure_ascii=False, indent=1)
    print('built', len(reg.TASKS), 'tasks')

def mod_of(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def validate(only=None, ncases=300):
    load_all()
    bad = 0
    for i, t in enumerate(reg.TASKS):
        if only and t['slug'] not in only: continue
        d = os.path.join(OUT, t['slug'])
        g = mod_of(d + '/gen.py', 'g' + t['slug']); s = mod_of(d + '/sol.py', 's' + t['slug']); b = mod_of(d + '/brute.py', 'b' + t['slug'])
        rnd = random.Random(777 + i)
        ok = True
        for c in range(ncases):
            inp = g.gen(rnd.randint(1, 8) if c % 3 else rnd.randint(8, 12), rnd, 0)
            if not inp.endswith('\n'): inp += '\n'
            try:
                a1 = s.sol(inp).strip(); a2 = b.brute(inp).strip()
            except Exception as e:
                print('ERR', t['slug'], repr(inp[:200]), repr(e)); ok = False; break
            if a1 != a2:
                print('DIFF', t['slug'], repr(inp[:200]), repr(a1[:50]), repr(a2[:50])); ok = False; break
        mt = 0; mx = 0
        if ok:
            for k in range(1, 11):
                rnd2 = random.Random((BASE + i) * 1000 + k)
                inp = g.gen(g.SIZES[k - 1], rnd2, k)
                if not inp.endswith('\n'): inp += '\n'
                mx = max(mx, len(inp))
                t0 = time.time(); s.sol(inp); mt = max(mt, time.time() - t0)
        print(('OK  ' if ok else 'FAIL'), t['slug'], 'maxsol=%.2fs maxin=%d' % (mt, mx))
        bad += (not ok)
    print('bad', bad)

if __name__ == '__main__':
    cmd = sys.argv[1]; only = set(sys.argv[2:]) or None
    if cmd == 'build': build(only)
    elif cmd == 'validate': validate(only)
    elif cmd == 'all': build(only); validate(only)
