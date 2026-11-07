import sys

d = sys.stdin.read().split()
P = 998244353
n, q = int(d[0]), int(d[1])
pos = 2
dist = [1]
for _ in range(n):
    k = int(d[pos])
    vals = [int(x) for x in d[pos + 1:pos + 1 + k]]
    pos += 1 + k
    ik = pow(k, P - 2, P)
    nd = [0] * (len(dist) + max(vals))
    for s, pr in enumerate(dist):
        if pr:
            for v in vals:
                nd[s + v] = (nd[s + v] + pr * ik) % P
    dist = nd
out = []
for _ in range(q):
    l, r = int(d[pos]), int(d[pos + 1])
    pos += 2
    out.append(sum(dist[l:r + 1]) % P)
print('\n'.join(map(str, out)))
