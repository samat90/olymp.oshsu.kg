import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 500); st = rng.choice([1, 5, 1000])
    a = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            b = max(a[i - 1][j] if i else 0, a[i][j - 1] if j else 0)
            a[i][j] = b + rng.randint(0, st)
    return '%d %d\n%s\n' % (n, rng.randint(1, n * n), '\n'.join(' '.join(map(str, r)) for r in a))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1585 * 100 + t), t))
