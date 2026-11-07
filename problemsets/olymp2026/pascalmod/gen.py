"""gen.py T maxN mode(small/tiny/mid/big/two/mixed/edge) maxE seed"""
import random
import sys

T, M, mode, E, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
random.seed(s * 1009 + T)


def is_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def prime(lo, hi):
    while True:
        v = random.randint(lo, hi)
        if is_prime(v):
            return v


out = []
for _ in range(T):
    if mode == 'tiny':
        p = random.choice([2, 3, 5, 7])
    elif mode == 'small':
        p = random.choice([2, 3, 5, 7, 11, 13, 101, 149])
    elif mode == 'two':
        p = random.choice([2, 2, 3])
    elif mode == 'mid':
        p = prime(2, 1000)
    elif mode == 'big':
        p = prime(10 ** 8, 10 ** 9)
    elif mode == 'edge':
        p = random.choice([2, 3, 999999937, 1000000007 - 10, 65537])
        p = p if is_prime(p) else 2
    else:
        p = random.choice([prime(2, 50), prime(2, 10 ** 5), prime(2, 10 ** 9)])
    if mode == 'edge':  # N near powers of p
        b = random.randint(1, 60)
        N = p ** b
        while N > M:
            N //= p
        N = max(1, N + random.randint(-2, 2))
    elif mode in ('small', 'tiny'):
        N = random.randint(1, M)
    else:
        N = random.randint(1, M) if random.random() < 0.7 else random.randint(M // 2, M)
    e = random.randint(1, E)
    out.append('%d %d %d' % (min(N, M), p, e))
print(T)
print('\n'.join(out))
