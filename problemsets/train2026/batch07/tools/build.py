import sys, os, re, json, random, time, glob, traceback
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = open(os.path.join(HERE, 'lib.py'), encoding='utf-8').read()
BATCH_BASE = 1728  # task number N -> code 00{1728+N}


def parse():
    tasks = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'src', '*.txt'))):
        txt = open(f, encoding='utf-8').read()
        for blk in re.split(r'^=== ', txt, flags=re.M)[1:]:
            head, _, rest = blk.partition('\n')
            n, name, topic, tl = [x.strip() for x in head.split('|')]
            parts = re.split(r'^--- (\w+)\n', rest, flags=re.M)
            t = {'n': int(n), 'name': name, 'topic': topic, 'tl': int(tl), 'samples': []}
            for i in range(1, len(parts), 2):
                key, val = parts[i], parts[i + 1]
                if key == 'sample':
                    t['samples'].append(val.strip('\n') + '\n')
                else:
                    t[key] = val.strip('\n') + '\n'
            tasks[t['n']] = t
    return tasks


def load(t):
    ns = {}
    exec(LIB + '\n' + t['code'], ns)
    return ns['gen'], ns['sol'], ns['brute']


def check(tasks, only, rounds=300):
    bad = 0
    for n in sorted(tasks):
        if only and n not in only:
            continue
        t = tasks[n]
        try:
            gen, sol, brute = load(t)
            for s in t['samples']:
                a, b = sol(s).strip(), brute(s).strip()
                assert a == b, 'sample mismatch %r vs %r' % (a, b)
            for i in range(rounds):
                r = random.Random(10**6 * n + i)
                inp = gen(r, 0)
                a, b = sol(inp).strip(), brute(inp).strip()
                assert a == b, 'MISMATCH on\n%s\nsol=%r brute=%r' % (inp, a, b)
            mx = 0; lst = []
            outs = set()
            for k in range(1, 11):
                r = random.Random(n * 1000 + k)
                inp = gen(r, k)
                st = time.time()
                a = sol(inp)
                mx = max(mx, time.time() - st)
                outs.add(a.strip()[:200]); lst.append(a.strip()[:10].replace('\n',' '))
                assert gen(random.Random(n * 1000 + k), k) == inp, 'gen not deterministic'
            print('OK  %3d %-40s max_sol=%.2fs distinct_outputs=%d %s' % (n, t['name'], mx, len(outs), '|'.join(lst)), flush=True)
        except Exception:
            bad += 1
            print('BAD %3d %s' % (n, t['name']))
            print(traceback.format_exc()[-1500:], flush=True)
    return bad


def emit(tasks, outdir):
    for n in sorted(tasks):
        t = tasks[n]
        gen, sol, brute = load(t)
        code = '%05d' % (BATCH_BASE + n) if False else '00%d' % (BATCH_BASE + n)
        d = os.path.join(outdir, 'p%03d' % n)
        os.makedirs(d, exist_ok=True)
        st = t['statement']
        for i, s in enumerate(t['samples']):
            o = sol(s)
            st += '\n### Пример %d\n\n**Ввод**\n```\n%s```\n\n**Вывод**\n```\n%s\n```\n' % (i + 1, s, o.strip())
            if 'note%d' % (i + 1) in t:
                st += '\n' + t['note%d' % (i + 1)]
        open(os.path.join(d, 'statement.md'), 'w', encoding='utf-8').write('# %s\n\n%s' % (t['name'], st))
        hdr = '# -*- coding: utf-8 -*-\n' + LIB + '\n' + t['code'] + '\n'
        open(os.path.join(d, 'gen.py'), 'w', encoding='utf-8').write(
            hdr + 'if __name__ == "__main__":\n    k = int(sys.argv[1])\n    print(gen(random.Random(%d * 1000 + k), k))\n' % n)
        for nm in ('sol', 'brute'):
            open(os.path.join(d, nm + '.py'), 'w', encoding='utf-8').write(
                hdr + 'if __name__ == "__main__":\n    print(%s(sys.stdin.read()))\n' % nm)
        json.dump({'code': code, 'name': t['name'], 'topic': t['topic'], 'time_limit': t['tl'],
                   'memory_mb': 256, 'points': 100, 'tests': 10, 'partial': True,
                   'gen': 'python3 gen.py K  (K=1..10)', 'seed': '%d*1000+K' % n},
                  open(os.path.join(d, 'meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    tasks = parse()
    mode = sys.argv[1]
    only = set(int(x) for x in sys.argv[2:])
    if mode == 'check':
        sys.exit(1 if check(tasks, only) else 0)
    elif mode == 'emit':
        emit(tasks, os.path.join(HERE, 'out'))
        print('emitted', len(tasks))
