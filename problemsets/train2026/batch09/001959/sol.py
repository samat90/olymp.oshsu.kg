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
    d = list(map(int, s.split()))
    n, m, k = d[:3]
    cells = sorted((d[3 + 2 * i], d[4 + 2 * i]) for i in range(k))
    N = n + m + 2
    f = [1] * N
    for i in range(1, N):
        f[i] = f[i - 1] * i % MOD
    inv = [1] * N
    inv[-1] = pow(f[-1], MOD - 2, MOD)
    for i in range(N - 1, 0, -1):
        inv[i - 1] = inv[i] * i % MOD
    def C(a, b):
        return f[a] * inv[b] % MOD * inv[a - b] % MOD if 0 <= b <= a else 0
    pts = cells + [(n, m)]
    dp = []
    for i, (x, y) in enumerate(pts):
        v = C(x + y - 2, x - 1)
        for j in range(i):
            xj, yj = pts[j]
            if xj <= x and yj <= y:
                v -= dp[j] * C(x - xj + y - yj, x - xj)
        dp.append(v % MOD)
    return str(dp[-1])


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
