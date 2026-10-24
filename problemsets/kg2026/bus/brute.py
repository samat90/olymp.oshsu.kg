import sys
d = sys.stdin.buffer.read().split()
p = 0
def nx():
    global p
    p += 1
    return int(d[p - 1])
n, m = nx(), nx()
c = [0] + [nx() for _ in range(n)]
trips = sorted([(nx(), nx(), nx(), nx()) for _ in range(m)], key=lambda x: x[2])
out = []
INF = float('inf')
for _ in range(nx()):
    t = nx()
    if n == 1:
        out.append(str(t)); continue
    ready = [INF] * (n + 1)
    ready[1] = t
    arr = INF
    for a, b, t1, t2 in trips:
        if ready[a] <= t1:
            if b == n:
                arr = min(arr, t2)
            ready[b] = min(ready[b], t2 + c[b])
    out.append(str(arr if arr < INF else -1))
print('\n'.join(out))
