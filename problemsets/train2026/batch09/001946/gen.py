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
        p = r.choice([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97])
        if p == 2:
            return "1 1 2\n" if False else "1 1 3\n"
        return "%d %d %d\n" % (r.randint(1, p - 1), r.randint(1, p - 1), p)
    p = r.choice([1000000007, 999999937, 998244353, 100000007, 1000003, 999983, 536870909, r.choice([999999893, 999999929])])
    if not is_prime(p):
        p = 1000000007
    a = r.randint(2, p - 1)
    if r.random() < 0.7:
        return "%d %d %d\n" % (a, pow(a, r.randint(0, p - 2), p), p)
    return "%d %d %d\n" % (a, r.randint(1, p - 1), p)


SEED = 1946

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(make(random.Random(SEED * 100 + t), t))
