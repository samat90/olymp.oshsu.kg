# Dijkstra over states (vertex, set of streets already cleaned): the shortest closed walk from 1.
import heapq
import sys

d = sys.stdin.read().split()
n, m = int(d[0]), int(d[1])
E = [(int(d[2 + 3 * i]), int(d[3 + 3 * i]), int(d[4 + 3 * i])) for i in range(m)]
adj = [[] for _ in range(n + 1)]
for i, (u, v, w) in enumerate(E):
    adj[u].append((v, w, i))
    adj[v].append((u, w, i))
full = (1 << m) - 1
dist = {(1, 0): 0}
pq = [(0, 1, 0)]
ans = None
while pq:
    dd, v, mask = heapq.heappop(pq)
    if dist.get((v, mask), None) != dd:
        continue
    if v == 1 and mask == full:
        ans = dd
        break
    for u, w, i in adj[v]:
        nm = mask | 1 << i
        if dd + w < dist.get((u, nm), float('inf')):
            dist[(u, nm)] = dd + w
            heapq.heappush(pq, (dd + w, u, nm))
print(ans)
