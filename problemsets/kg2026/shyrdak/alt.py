# Independent check in exact integer arithmetic: sum modulo P*n, then exact division by n.
import math
import random
import sys

P = 10 ** 9 + 7
SMALL = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(n):
    if n < 2:
        return False
    for p in SMALL:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in SMALL:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def brent(n):
    if n % 2 == 0:
        return 2
    while True:
        y, c, m = random.randrange(1, n), random.randrange(1, n), 64
        g = r = q = 1
        x = ys = y
        while g == 1:
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                g = math.gcd(q, n)
                k += m
            r *= 2
        if g == n:
            while True:
                ys = (ys * ys + c) % n
                g = math.gcd(abs(x - ys), n)
                if g > 1:
                    break
        if g != n:
            return g


def factor(n, out):
    if n == 1:
        return
    if is_prime(n):
        out[n] = out.get(n, 0) + 1
        return
    for p in SMALL:
        if n % p == 0:
            out[p] = out.get(p, 0) + 1
            factor(n // p, out)
            return
    d = brent(n)
    factor(d, out)
    factor(n // d, out)


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    res = []
    for i in range(t):
        n, k = int(data[1 + 2 * i]), int(data[2 + 2 * i])
        f = {}
        factor(n, f)
        primes = list(f.items())
        mod = P * n
        divisors = [(1, (k - 1) % mod)]
        for p, a in primes:
            nxt = []
            for d, xd in divisors:
                for e in range(a + 1):
                    nxt.append((d, xd))
                    d, xd = d * p, pow(xd, p, mod)
            divisors = nxt
        total = 0
        for d, xd in divisors:
            m = n // d
            ph = m
            for p, _ in primes:
                if m % p == 0:
                    ph = ph // p * (p - 1)
            total += ph * (xd + (k - 1 if d % 2 == 0 else -(k - 1)))
        total %= mod
        assert total % n == 0
        res.append(str(total // n % P))
    print('\n'.join(res))


main()
