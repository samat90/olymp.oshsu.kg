"""gen.py T maxAB mode(small/half/rand/skew/edge) seed
Cases where x^(a+b) = (y-x)^(a+b) mod P are skipped (the statement guarantees they do not occur)."""
import random
import sys

T, M, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 4049 + T)
P = 998244353
out = []
while len(out) < T:
    if mode == 'small':
        a = random.randint(1, M - 1)
        b = random.randint(1, max(1, M - a))
    else:
        a, b = random.randint(1, M), random.randint(1, M)
        if mode == 'edge':
            a = random.choice([1, 2, M, M - 1, P - 1, P, P + 1, 2 * (P - 1)])
            a = min(M, max(1, a))
    y = random.randint(2, 10 ** 9) if mode not in ('small',) else random.randint(2, 12)
    x = random.randint(1, y - 1)
    if mode == 'half' and random.random() < 0.6:
        y = 2 * random.randint(1, 5 * 10 ** 8)
        x = y // 2
    if mode == 'skew':
        x = random.choice([1, y - 1, x])
    if 2 * x != y and (pow(x, a + b, P) - pow(y - x, a + b, P)) % P == 0:
        continue
    out.append('%d %d %d %d' % (a, b, x, y))
print(T)
print('\n'.join(out))
