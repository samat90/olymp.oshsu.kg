"""gen.py T maxV mode(rand/near/pos/diag/edge) seed"""
import math
import random
import sys

T, M, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 9091 + T)


def A(k):
    return (k + math.isqrt(5 * k * k)) // 2


out = []
for _ in range(T):
    kmax = max(1, int(M / 2.62))
    k = random.randint(0, kmax)
    a, b = A(k), A(k) + k
    if mode == 'rand':
        a, b = random.randint(0, M), random.randint(0, M)
    elif mode == 'near':  # one step from a losing position
        r = random.random()
        t = random.randint(1, 3)
        if r < 0.33:
            a += t
        elif r < 0.66:
            b += t
        else:
            a += t
            b += t
    elif mode == 'diag':
        a = random.randint(0, M)
        b = a + random.randint(-3, 3)
    elif mode == 'edge':
        a = random.choice([0, 1, M, A(kmax), A(kmax) + kmax])
        b = random.choice([0, 1, M, random.randint(0, M), A(kmax)])
    if random.random() < 0.5:
        a, b = b, a
    a, b = min(M, max(0, a)), min(M, max(0, b))
    out.append('%d %d' % (a, b))
print(T)
print('\n'.join(out))
