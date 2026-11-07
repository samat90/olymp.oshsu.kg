import sys

d = sys.stdin.read().split()
n = int(d[0])
g = [[] for _ in range(n + 1)]
for i in range(n - 1):
    u, v, w = int(d[1 + 3 * i]), int(d[2 + 3 * i]), int(d[3 + 3 * i])
    g[u].append((v, w))
    g[v].append((u, w))
best = None
for c in range(1, n + 1):
    dist = {c: 0}
    st = [c]
    while st:
        v = st.pop()
        for u, w in g[v]:
            if u not in dist:
                dist[u] = dist[v] + w
                st.append(u)
    s = sum(x * x for x in dist.values())
    if best is None or s < best[1]:
        best = (c, s)
print(best[0], best[1])
