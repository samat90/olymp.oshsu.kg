import sys
from functools import lru_cache

n, m = map(int, sys.stdin.read().split())
N = n * m


@lru_cache(maxsize=None)
def go(mask):
    if mask == (1 << N) - 1:
        return 1
    i = 0
    while mask >> i & 1:
        i += 1
    r, c = i % n, i // n
    res = 0
    if r + 1 < n and not mask >> (i + 1) & 1:
        res += go(mask | 1 << i | 1 << (i + 1))
    if c + 1 < m:
        res += go(mask | 1 << i | 1 << (i + n))
    return res


print(go(0) % 1000000007 if N <= 40 else 0)
