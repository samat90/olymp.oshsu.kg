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

def solve(s):
    a, p = map(int, s.split())
    if a == 0:
        return "0"
    if pow(a, (p - 1) // 2, p) != 1:
        return "-1"
    q, e = p - 1, 0
    while q % 2 == 0:
        q //= 2; e += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, R = e, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, tt = 0, t
        while tt != 1:
            tt = tt * tt % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, R = i, b * b % p, t * b * b % p, R * b % p
    return str(min(R, p - R))


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
