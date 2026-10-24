"""gen.py n m q cmax tmax mode(lines/random/chain) seed

lines: a random road tree; bus lines run back and forth along walks in it (many along the
       road from stop 1 to stop n), every line repeats during the day with its own period.
chain: one relay through all stops, queries mostly before it starts.
random: independent random trips.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, write  # noqa: E402

n, m, q, cmax, tmax, mode, s = [int(x) for x in sys.argv[1:6]] + sys.argv[6:8]
seed(s)
c = [random.randint(0, cmax) for _ in range(n + 1)]
c[0] = 0
trips = []
qmax = tmax
if mode == 'chain':
    t0 = t = random.randint(tmax // 2, tmax // 2 + tmax // 10)
    order = [1] + random.sample(range(2, n), n - 2) + [n] if n > 2 else [1, n]
    for i in range(len(order) - 1):
        t += random.randint(0, 3)
        t2 = t + random.randint(1, 5)
        trips.append((order[i], order[i + 1], t, t2))
        t = t2 + c[order[i + 1]]
    qmax = t0 + 2
elif mode == 'lines':
    par = [0, 0] + [random.randint(max(1, i - random.choice([1, 2, 5, 1000, 100000])), i - 1) for i in range(2, n + 1)]
    deep = n
    perm = [0, 1] + random.sample(range(2, n), n - 2) + [n]
    adj = [[] for _ in range(n + 1)]
    for v in range(2, n + 1):
        adj[v].append(par[v]); adj[par[v]].append(v)
    main_path = []
    v = deep
    while v:
        main_path.append(v)
        v = par[v]
    main_path.reverse()
    w = {}
    while len(trips) < m:
        if random.random() < 0.5 and len(main_path) > 1:
            i = random.randrange(len(main_path) - 1)
            j = random.randint(i + 1, min(len(main_path) - 1, i + 60))
            walk = main_path[i:j + 1]
            if random.random() < 0.3:
                walk.reverse()
        else:
            walk = [random.randint(1, n)]
            for _ in range(random.randint(1, 40)):
                walk.append(random.choice(adj[walk[-1]]))
        period = max(1, tmax // random.randint(1, max(1, min(40, m // 2000))))
        start = random.randint(0, period)
        while start < tmax and len(trips) < m:
            t = start
            for a, b in zip(walk, walk[1:]):
                key = (min(a, b), max(a, b))
                if key not in w:
                    w[key] = random.randint(1, max(1, tmax // 3000))
                t2 = t + w[key] + random.randint(0, 2)
                if t2 > tmax:
                    break
                trips.append((perm[a], perm[b], t, t2))
                t = t2 + c[perm[b]] + random.randint(0, 2)  # the bus waits long enough to change
            start += period + random.randint(0, period // 10)
while len(trips) < m:
    a, b = random.sample(range(1, n + 1), 2)
    t1 = random.randint(0, tmax - 1)
    trips.append((a, b, t1, random.randint(t1 + 1, min(tmax, t1 + max(1, tmax // 100)))))
trips = trips[:m]
random.shuffle(trips)
lines = ['%d %d' % (n, len(trips)), ' '.join(map(str, c[1:]))]
lines += ['%d %d %d %d' % x for x in trips]
lines.append(str(q))
lines += [str(random.randint(0, qmax)) for _ in range(q)]
write(lines)
