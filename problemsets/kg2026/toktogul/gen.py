"""gen.py n m cmax wmax lower(0/1) mode(feasible/tight/infeasible/random) seed

A random network of canals from reservoir 1 to station n. In the feasible modes a real flow is
sent first and lower bounds are taken below it, so a solution is guaranteed to exist.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, write  # noqa: E402

n, m, cmax, wmax, lower = [int(x) for x in sys.argv[1:6]]
mode, s = sys.argv[6], sys.argv[7]
seed(s)
# nodes ordered roughly by altitude: canals mostly go downhill, some go back (pumps)
edges = []
for i in range(1, n):
    edges.append([i, i + 1])
while len(edges) < m:
    a, b = random.sample(range(1, n + 1), 2)
    if random.random() < 0.8 and a > b:
        a, b = b, a
    edges.append([a, b])
random.shuffle(edges)
adj = [[] for _ in range(n + 1)]
for i, (a, b) in enumerate(edges):
    adj[a].append(i)
flow = [0] * len(edges)
F = 0
# send water along random walks from 1 to n (walks that reach n)
for _ in range(max(1, m // 2)):
    path, v, seen = [], 1, {1}
    for _ in range(4 * n):
        if v == n:
            break
        opts = [i for i in adj[v] if edges[i][1] not in seen]
        if not opts:
            break
        i = random.choice(opts)
        path.append(i)
        v = edges[i][1]
        seen.add(v)
    if v != n or n == 1:
        continue
    amount = random.randint(1, max(1, cmax // 4))
    for i in path:
        flow[i] += amount
    F += amount
lines = []
for i, (a, b) in enumerate(edges):
    f = flow[i]
    if mode == 'random':
        c = random.randint(0, cmax)
        l = random.randint(0, c) if lower and random.random() < 0.3 else 0
    else:
        c = max(f, random.randint(0, cmax)) if mode != 'tight' else f + random.randint(0, 2)
        l = random.randint(0, f) if lower else 0
    lines.append('%d %d %d %d %d' % (a, b, l, c, random.randint(0, wmax)))
if mode == 'infeasible':
    F += random.randint(1, 10 ** 6)
elif mode == 'random':
    F = random.randint(0, max(1, F))
write(['%d %d %d' % (n, len(lines), F)] + lines)
