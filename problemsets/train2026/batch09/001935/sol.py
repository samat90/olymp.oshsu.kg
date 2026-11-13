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
    d = s.split(); n = int(d[0]); a = list(map(int, d[1:1 + n]))
    M = max(a)
    cnt = [0] * (M + 1)
    for x in a:
        cnt[x] += 1
    mu = [1] * (M + 1)
    isp = bytearray([1]) * (M + 1)
    for i in range(2, M + 1):
        if isp[i]:
            for j in range(i, M + 1, i):
                if j > i:
                    isp[j] = 0
                mu[j] = -mu[j]
            sq = i * i
            for j in range(sq, M + 1, sq):
                mu[j] = 0
    tot = 0
    for dd in range(1, M + 1):
        if mu[dd]:
            c = sum(cnt[dd::dd])
            tot += mu[dd] * c * (c - 1) // 2
    return str(tot)


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
