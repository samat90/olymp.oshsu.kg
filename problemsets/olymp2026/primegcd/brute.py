import sys
from math import gcd

d = sys.stdin.read().split()
q = int(d[0])
M = 2000
isp = [False, False] + [True] * (M - 1)
for i in range(2, M + 1):
    if isp[i]:
        for j in range(i * i, M + 1, i):
            isp[j] = False
out = []
for t in range(q):
    A, B = int(d[1 + 2 * t]), int(d[2 + 2 * t])
    out.append(sum(1 for x in range(1, A + 1) for y in range(1, B + 1) if isp[gcd(x, y)]))
print('\n'.join(map(str, out)))
