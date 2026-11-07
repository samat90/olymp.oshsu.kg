import sys

sys.setrecursionlimit(10000)
d = sys.stdin.read().split()
n, m = int(d[0]), int(d[1])
a = [int(d[2 + 2 * i]) for i in range(m)]
b = [int(d[3 + 2 * i]) for i in range(m)]
used = [False] * m
used[0] = True


def go(v, k):
    if k == m:
        return 1 if v == a[0] else 0
    r = 0
    for i in range(m):
        if not used[i] and a[i] == v:
            used[i] = True
            r += go(b[i], k + 1)
            used[i] = False
    return r


print(go(b[0], 1) % 1000000007)
