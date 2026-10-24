# Exhaustive game search over multisets of positions (tiny tests only).
import sys
from functools import lru_cache
sys.setrecursionlimit(100000)
d = sys.stdin.read().split()
p = 0
def nx():
    global p
    p += 1
    return int(d[p - 1])
n, m = nx(), nx()
adj = [[] for _ in range(n + 1)]
for _ in range(m):
    a, b = nx(), nx()
    adj[a].append(b)

@lru_cache(maxsize=None)
def win(state):
    for i, v in enumerate(state):
        for u in adj[v]:
            nxt = tuple(sorted(state[:i] + (u,) + state[i + 1:]))
            if not win(nxt):
                return True
    return False

out = []
for _ in range(nx()):
    k = nx()
    st = tuple(nx() for _ in range(k))
    cnt = 0
    for i, v in enumerate(st):
        for u in adj[v]:
            if not win(tuple(sorted(st[:i] + (u,) + st[i + 1:]))):
                cnt += 1
    out.append(str(cnt))
print('\n'.join(out))
