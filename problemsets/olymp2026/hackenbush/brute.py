import sys
from functools import lru_cache

d = sys.stdin.read().split()
n = int(d[0])
p = [0] + [int(x) for x in d[1:1 + n]]
desc = [1 << v for v in range(n + 1)]
for v in range(n, 0, -1):
    desc[p[v]] |= desc[v]


@lru_cache(maxsize=None)
def win(alive):
    # alive: bit mask of vertices still attached (vertex 0 always alive)
    x = alive & ~1
    while x:
        v = (x & -x).bit_length() - 1
        x &= x - 1
        if not win(alive & ~desc[v]):
            return True
    return False


full = (1 << (n + 1)) - 1
cnt = 0
for v in range(1, n + 1):
    if not win(full & ~desc[v]):
        cnt += 1
print(cnt)
