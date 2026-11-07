import sys
from math import comb

d = sys.stdin.read().split()
T = int(d[0])
out = []
for t in range(T):
    N, p, e = int(d[1 + 3 * t]), int(d[2 + 3 * t]), int(d[3 + 3 * t])
    m = p ** e
    cnt = 0
    for n in range(N):
        for k in range(n + 1):
            if comb(n, k) % m == 0:
                cnt += 1
    out.append(cnt % 1000000007)
print('\n'.join(map(str, out)))
