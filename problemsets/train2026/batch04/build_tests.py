# Строит тесты партии 4: python build_tests.py <папка_партии> <выходная_папка>
# Для каждой задачи: tests/NN.in и tests/NN.out (NN = 01..10) по meta.json (seed_base + номер теста, уровни test_levels).
import json, os, subprocess, sys
src, dst = sys.argv[1], sys.argv[2]
for code in sorted(x for x in os.listdir(src) if x.isdigit()):
    d = os.path.join(src, code); m = json.load(open(d + '/meta.json'))
    o = os.path.join(dst, code); os.makedirs(o, exist_ok=True)
    for t in range(1, m['tests'] + 1):
        seed = m['seed_base'] + t; lvl = m['test_levels'][t - 1]
        inp = subprocess.run([sys.executable, d + '/gen.py', str(seed), str(lvl)], capture_output=True, text=True, check=True).stdout
        out = subprocess.run([sys.executable, d + '/sol.py'], input=inp, capture_output=True, text=True, check=True).stdout
        open('%s/%02d.in' % (o, t), 'w').write(inp); open('%s/%02d.out' % (o, t), 'w').write(out)
    print(code, 'ok')
