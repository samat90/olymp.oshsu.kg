import sys, math, itertools, random
from math import gcd, isqrt, comb, factorial
from itertools import *
from fractions import Fraction
MOD = 10**9 + 7

def is_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
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

def sieve(n):
    s = bytearray([1]) * (n + 1)
    s[0] = 0
    if n >= 1:
        s[1] = 0
    for i in range(2, isqrt(n) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(range(i * i, n + 1, i)))
    return s

def primes_upto(n):
    s = sieve(n)
    return [i for i in range(n + 1) if s[i]]

_PR = []
def factor(n):
    """n <= 1e12 (works for larger n whose cofactor is prime)"""
    global _PR
    if not _PR:
        _PR = primes_upto(10**6)
    f = {}
    for p in _PR:
        if p * p > n:
            break
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            f[p] = e
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f

def make(r, k):
    def lcm(a, b):
        return a // gcd(a, b) * b
    if k <= 3:
        n = r.randint(1, 3); mx = [8, 12, 15][k - 1]
        while True:
            ms = [r.randint(1, mx) for _ in range(n)]
            L = 1
            for m in ms:
                L = lcm(L, m)
            if L <= 2000:
                break
        rs = [r.randint(0, m - 1) for m in ms]
        if r.random() < 0.6:
            x = r.randint(0, L - 1)
            rs = [x % m for m in ms]
    else:
        n = [3, 5, 8, 12, 15, 20, 20][k - 4]
        while True:
            ms = []
            L = 1
            for _ in range(n):
                m = r.choice([r.randint(2, 10**9), r.randint(2, 1000), 2 ** r.randint(1, 29), 3 ** r.randint(1, 18)])
                if lcm(L, m) <= 10**18:
                    L = lcm(L, m); ms.append(m)
            if ms:
                break
        x = r.randint(0, L - 1)
        rs = [x % m for m in ms]
        if r.random() < 0.3:
            i = r.randrange(len(ms)); rs[i] = r.randint(0, ms[i] - 1)
        n = len(ms)
    return "%d\n%s\n" % (n, "\n".join("%d %d" % (a, b) for a, b in zip(rs, ms)))


SEED = 1947

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(make(random.Random(SEED * 100 + t), t))
