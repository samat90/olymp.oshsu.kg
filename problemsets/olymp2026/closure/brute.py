import sys

d = sys.stdin.read().split()
n, m = int(d[0]), int(d[1])
p = [int(x) for x in d[2:2 + n]]
need = [0] * n
for i in range(m):
    a, b = int(d[2 + n + 2 * i]) - 1, int(d[3 + n + 2 * i]) - 1
    need[a] |= 1 << b
best = 0
for mask in range(1 << n):
    ok = True
    s = 0
    for i in range(n):
        if mask >> i & 1:
            if need[i] & ~mask:
                ok = False
                break
            s += p[i]
    if ok and s > best:
        best = s
print(best)
