import sys
from itertools import permutations

d = sys.stdin.read().split()
T = int(d[0])
out = []
for t in range(T):
    n = int(d[1 + t])
    M = 2 * n
    cnt = 0
    # women on even seats in some order, men on odd seats; the other parity is symmetric (factor 2)
    for women in permutations(range(n)):
        for men in permutations(range(n)):
            ok = True
            for i in range(n):
                w = women[i]
                left, right = men[i - 1], men[i]  # seats 2i-1 and 2i+1 (cyclic)
                if left == w or right == w:
                    ok = False
                    break
            if ok:
                cnt += 1
    out.append(2 * cnt % 1000000007)
print('\n'.join(map(str, out)))
