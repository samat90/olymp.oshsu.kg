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
    if k <= 3:
        n = r.randint(1, 4); m = [10, 30, 30][k - 1]
    else:
        n = [50, 1000, 20000, 50000, 100000, 100000, 100000][min(k - 4, 6)]; m = 10**6
    a = [r.randint(1, m) for _ in range(n)]
    if k >= 7:
        a = [r.choice([720720, 997 * 991, 2**19, 999983, 3**12, r.randint(1, m)]) for _ in range(n)]
    return "%d\n%s\n" % (n, " ".join(map(str, a)))


SEED = 1930

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(make(random.Random(SEED * 100 + t), t))
