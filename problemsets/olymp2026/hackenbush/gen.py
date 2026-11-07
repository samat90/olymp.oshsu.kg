"""gen.py n shape seed: vertex numbers are relabelled so that every parent has a smaller number"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, tree  # noqa: E402

n, shape, s = int(sys.argv[1]), sys.argv[2], sys.argv[3]
seed(s)
# a tree on n + 1 vertices, vertex 0 = the ground
edges = tree(n + 1, shape, shuffle=False)
adj = [[] for _ in range(n + 2)]
for a, b in edges:
    adj[a].append(b)
    adj[b].append(a)
root = 1 if shape not in ('star',) or random.random() < 0.5 else random.randint(1, n + 1)
order, par, seen = [], {root: 0}, {root}
queue = [root]
while queue:  # BFS order: parents first
    v = queue.pop(random.randrange(len(queue))) if random.random() < 0.3 else queue.pop()
    order.append(v)
    for u in adj[v]:
        if u not in seen:
            seen.add(u)
            par[u] = v
            queue.append(u)
num = {v: i for i, v in enumerate(order)}
p = [0] * (n + 1)
for v in order[1:]:
    p[num[v]] = num[par[v]]
print(n)
print(' '.join(map(str, p[1:])))
