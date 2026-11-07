"""gen.py T maxM mode(rand/pow/square/semiprime/smooth/zero) seed"""
import random
import sys

T, M, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 3571 + T)


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
    if mode == 'pow':
        p = random.choice([2, 2, 3, 5, 7])
        m = p
        while m * p <= M and random.random() < 0.9:
            m *= p
        if random.random() < 0.3 and M > 10 ** 6:
            m *= prime(2, max(2, M // m)) if M // m >= 2 else 1
    elif mode == 'semiprime' and M > 10 ** 9:
        m = prime(10 ** 8, 10 ** 9) * prime(10 ** 8, 10 ** 9)
        if random.random() < 0.3:
            q = prime(10 ** 5, 10 ** 6)
            m = q * q * prime(2, M // (q * q))
    elif mode == 'smooth':
        m = 1
        while True:
            p = random.choice([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43])
            if m * p > M:
                break
            m *= p
    else:
        m = random.randint(1, M)
    m = min(m, M)
    if mode in ('square', 'smooth', 'pow', 'semiprime') or random.random() < 0.5:
        x = random.randrange(m)
        if random.random() < 0.3:  # x shares factors with m
            g = random.choice([2, 3, 4, 8, 9, 16, 27])
            x = x // g * g
        a = x * x % m
    else:
        a = random.randrange(m)
    if mode == 'zero' and random.random() < 0.5:
        p = random.choice([2, 3, 5])
        k = random.randint(1, 30)
        m = min(M, p ** k * random.randint(1, 1000))
        a = (p ** random.randint(0, k)) % m
    out.append('%d %d' % (a, m))
print(T)
print('\n'.join(out))
