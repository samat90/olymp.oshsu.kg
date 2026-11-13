import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); hi = rng.choice([3, 10**9])
    a = [rng.randint(-hi, hi) for _ in range(n)]
    if rng.random() < 0.4:
        a.sort()
        for _ in range(rng.randint(0, max(1, n // 5))):
            i = rng.randrange(n); j = min(n - 1, i + rng.randint(0, 3)); a[i], a[j] = a[j], a[i]
    return '%d\n%s\n' % (n, ' '.join(map(str, a)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1624 * 100 + t), t))
