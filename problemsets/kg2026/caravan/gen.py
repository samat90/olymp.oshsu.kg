"""gen.py n shape lmax smax vmax seed  (shapes from genlib.tree, rooted at city 1)"""
import os
import random
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, tree, write  # noqa: E402

n, shape = int(sys.argv[1]), sys.argv[2]
lmax, smax, vmax, s = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
seed(s)
edges = tree(n, shape) if n > 1 else []
adj = [[] for _ in range(n + 1)]
for a, b in edges:
    adj[a].append(b)
    adj[b].append(a)
par = [0] * (n + 1)
seen = [False] * (n + 1)
seen[1] = True
dq = deque([1])
while dq:
    v = dq.popleft()
    for u in adj[v]:
        if not seen[u]:
            seen[u] = True
            par[u] = v
            dq.append(u)
lines = [str(n)]
for i in range(2, n + 1):
    # cities far from Osh tend to have slow messengers and quick preparation, or the reverse
    lines.append('%d %d %d %d' % (par[i], random.randint(1, lmax), random.randint(0, smax), random.randint(1, vmax)))
write(lines)
