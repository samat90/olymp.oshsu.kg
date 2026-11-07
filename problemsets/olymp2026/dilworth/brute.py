# Largest antichain by trying all subsets (Dilworth's theorem says it equals the answer).
import sys

d = sys.stdin.read().split()
n, m = int(d[0]), int(d[1])
R = [[False] * n for _ in range(n)]
for i in range(m):
    R[int(d[2 + 2 * i]) - 1][int(d[3 + 2 * i]) - 1] = True
for k in range(n):
    for i in range(n):
        if R[i][k]:
            for j in range(n):
                if R[k][j]:
                    R[i][j] = True
comp = [0] * n
for i in range(n):
    for j in range(n):
        if R[i][j] or R[j][i]:
            comp[i] |= 1 << j
best = 0
for mask in range(1 << n):
    c = bin(mask).count('1')
    if c <= best:
        continue
    ok = True
    x = mask
    while x:
        i = (x & -x).bit_length() - 1
        if comp[i] & mask:
            ok = False
            break
        x &= x - 1
    if ok:
        best = c
print(best)
