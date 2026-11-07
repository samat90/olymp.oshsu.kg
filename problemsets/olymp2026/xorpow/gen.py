"""gen.py B n K q seed"""
import random
import sys

B, n, K, q, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
random.seed(s * 7333 + n)
S = 1 << B
mode = random.random()
if mode < 0.3:  # codes from a small subspace: many targets are unreachable
    basis = [random.randrange(S) for _ in range(max(1, B // 2))]
    a = []
    for _ in range(n):
        v = 0
        for b in basis:
            if random.random() < 0.5:
                v ^= b
        a.append(v)
else:
    a = [random.randrange(S) for _ in range(n)]
xs = [random.randrange(S) for _ in range(q)]
print(B, n, K, q)
print(' '.join(map(str, a)))
print(' '.join(map(str, xs)))
