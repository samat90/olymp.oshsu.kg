"""gen.py k N mode(rand/low/zero/fib/poly) seed: hidden recurrence of order L <= k"""
import random
import sys

k, N, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 8111 + k)
P = 998244353
if mode == 'low':
    L = random.randint(1, max(1, k // 3))
elif mode == 'fib':
    L = 2
else:
    L = random.randint(max(1, k - 2), k) if random.random() < 0.7 else random.randint(1, k)
if mode == 'fib':
    c = [1, 1]
    init = [random.randint(0, P - 1), random.randint(0, P - 1)]
elif mode == 'poly':  # a[i] = polynomial of degree L-1: characteristic (x-1)^L
    from math import comb
    c = [(-1) ** (j + 1) * comb(L, j) % P for j in range(1, L + 1)]
    init = [random.randint(0, P - 1) for _ in range(L)]
else:
    c = [random.randint(0, P - 1) for _ in range(L)]
    if mode == 'zero':  # sparse coefficients, some zeros at the end (smaller real order)
        c = [x if random.random() < 0.3 else 0 for x in c]
        c[random.randrange(L)] = random.randint(1, P - 1)
    init = [random.randint(0, P - 1) for _ in range(L)]
seq = init[:]
while len(seq) < 2 * k:
    i = len(seq)
    seq.append(sum(c[j] * seq[i - 1 - j] for j in range(L)) % P)
print(k, N)
print(' '.join(map(str, seq[:2 * k])))
