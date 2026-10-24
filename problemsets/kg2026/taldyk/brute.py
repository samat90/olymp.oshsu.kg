import sys
from collections import deque
d = sys.stdin.buffer.read().split()
p = 0
def nx():
    global p
    p += 1
    return int(d[p - 1])
n, m = nx(), nx()
h = [0] + [nx() for _ in range(n)]
adj = [[] for _ in range(n + 1)]
for _ in range(m):
    a, b, w = nx(), nx(), nx()
    adj[a].append((b, w)); adj[b].append((a, w))
last = 0
out = []
for _ in range(nx()):
    v, W, k = nx() ^ last, nx() ^ last, nx() ^ last
    seen = {v}
    dq = deque([v])
    while dq:
        x = dq.popleft()
        for y, w in adj[x]:
            if w >= W and y not in seen:
                seen.add(y); dq.append(y)
    vals = sorted((h[x] for x in seen), reverse=True)
    ans = vals[k - 1] if k <= len(vals) else -1
    last = ans if ans != -1 else 0
    out.append(str(ans))
print('\n'.join(out))
