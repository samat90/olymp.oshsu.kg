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
    n = r.randint(2, [4, 6, 8][k - 1]) if k <= 3 else [100, 1000, 10000, 50000, 100000, 100000, 100000][k - 4]
    m = [8, 16, 64][k - 1] if k <= 3 else 2**30
    perm = list(range(1, n + 1))
    r.shuffle(perm)
    lines = []
    for i in range(1, n):
        p = r.randint(max(0, i - 3), i - 1) if k % 2 == 0 and k > 3 else r.randint(0, i - 1)
        lines.append("%d %d %d" % (perm[p], perm[i], r.randrange(m)))
    r.shuffle(lines)
    return "%d\n%s\n" % (n, "\n".join(lines))


SEED = 2008

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(make(random.Random(SEED * 100 + t), t))
