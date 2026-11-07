import sys

d = sys.stdin.read().split()
n, q = int(d[0]), int(d[1])
c = [int(x) for x in d[2:2 + n]]
pos = 2 + n
out = []
for _ in range(q):
    t, x, y = int(d[pos]), int(d[pos + 1]), int(d[pos + 2])
    pos += 3
    if t == 1:
        c[x - 1] = y
    else:
        cnt = {}
        for v in c[x - 1:y]:
            cnt[v] = cnt.get(v, 0) + 1
        out.append(sum(v * v for v in cnt.values()))
print('\n'.join(map(str, out)))
