import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); hi = rng.choice([2, 10**9])
    h = [rng.randint(0, hi) for _ in range((n + 1) // 2)]
    a = h + h[:n // 2][::-1]
    if rng.random() < 0.5: a[rng.randrange(n)] = rng.randint(0, hi)
    return '%d\n%s\n' % (n, ' '.join(map(str, a)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1601 * 100 + t), t))
