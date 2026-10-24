import sys
from collections import deque


def main():
    data = sys.stdin.buffer.read().split()
    it = iter(data)
    n = int(next(it))
    h = [0] + [int(next(it)) for _ in range(n)]
    g = [[] for _ in range(n + 1)]
    for _ in range(n - 1):
        a, b = int(next(it)), int(next(it))
        g[a].append(b)
        g[b].append(a)
    par = [0] * (n + 1)
    dep = [0] * (n + 1)
    seen = [False] * (n + 1)
    dq = deque([1])
    seen[1] = True
    while dq:
        v = dq.popleft()
        for u in g[v]:
            if not seen[u]:
                seen[u] = True
                par[u] = v
                dep[u] = dep[v] + 1
                dq.append(u)
    out = []
    for _ in range(int(next(it))):
        t = int(next(it))
        if t == 1:
            v, x = int(next(it)), int(next(it))
            h[v] = x
        else:
            a, b = int(next(it)), int(next(it))
            vals = []
            while a != b:
                if dep[a] < dep[b]:
                    a, b = b, a
                vals.append(h[a])
                a = par[a]
            vals.append(h[a])
            m = max(vals)
            out.append('%d %d' % (m, vals.count(m)))
    print('\n'.join(out))


main()
