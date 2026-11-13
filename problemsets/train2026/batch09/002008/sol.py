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
    n = d[0]
    adj = [[] for _ in range(n + 1)]
    for i in range(n - 1):
        u, v, w = d[1 + 3 * i:4 + 3 * i]
        adj[u].append((v, w)); adj[v].append((u, w))
    dist = [0] * (n + 1)
    seen = [False] * (n + 1)
    seen[1] = True
    st = [1]
    while st:
        u = st.pop()
        for v, w in adj[u]:
            if not seen[v]:
                seen[v] = True
                dist[v] = dist[u] ^ w
                st.append(v)
    t = 0
    xs = dist[1:]
    for b in range(30):
        c1 = sum(1 for x in xs if x >> b & 1)
        t += c1 * (n - c1) << b
    return str(t)


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
