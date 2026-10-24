"""gen.py n m q hmax wmax kmode(one/small/any) shape(random/path/sparse) seed

Queries are encoded with the answers of the reference solution (compiled with -DRAW).
"""
import hashlib
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from genlib import seed  # noqa: E402

n, m, q, hmax, wmax = [int(x) for x in sys.argv[1:6]]
kmode, shape, s = sys.argv[6], sys.argv[7], sys.argv[8]
seed(s)
h = [random.randint(1, hmax) for _ in range(n)]
edges = []
if shape == 'path':
    order = random.sample(range(1, n + 1), n)
    edges = [(order[i], order[i + 1]) for i in range(n - 1)]
elif shape != 'sparse':
    for i in range(2, n + 1):
        edges.append((random.randint(max(1, i - 50), i - 1), i))
while len(edges) < m:
    a, b = random.randint(1, n), random.randint(1, n)
    if a != b:
        edges.append((a, b))
edges = edges[:m]
random.shuffle(edges)
ws = [random.randint(1, wmax) for _ in edges]
queries = []
for _ in range(q):
    v = random.randint(1, n)
    W = random.randint(1, wmax + 1) if random.random() < 0.9 else random.choice([1, wmax, wmax + 1])
    if kmode == 'one':
        k = 1
    elif kmode == 'small':
        k = random.randint(1, 5)
    else:
        k = random.choice([1, 2, random.randint(1, 50), random.randint(1, n)])
    queries.append((v, W, k))
head = ['%d %d' % (n, m), ' '.join(map(str, h))] + ['%d %d %d' % (a, b, w) for (a, b), w in zip(edges, ws)]
raw = '\n'.join(head + [str(q)] + ['%d %d %d' % x for x in queries]) + '\n'

src = os.path.join(HERE, 'sol.cpp')
exe = '/tmp/taldyk_raw_' + hashlib.sha1(open(src, 'rb').read()).hexdigest()[:10]
if not os.path.exists(exe):
    subprocess.run(['g++', '-O2', '-w', '-DRAW', '-o', exe, src], check=True)
answers = subprocess.run([exe], input=raw.encode(), stdout=subprocess.PIPE, check=True).stdout.split()
last = 0
enc = []
for (v, W, k), a in zip(queries, answers):
    enc.append('%d %d %d' % (v ^ last, W ^ last, k ^ last))
    a = int(a)
    last = a if a != -1 else 0
sys.stdout.write('\n'.join(head + [str(q)] + enc) + '\n')
