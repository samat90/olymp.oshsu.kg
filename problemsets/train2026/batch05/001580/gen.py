import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000) - 2; n = max(n, 0)
    T = rng.choice([30, 10**9]); xs = sorted(rng.sample(range(1, T), min(n, T - 1)))
    F = rng.randint(0, T // 3)
    return '%d %d %d\n%s\n' % (T, F, len(xs), '\n'.join('%d %d' % (x, rng.randint(1, T // 4 + 1)) for x in xs))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1580 * 100 + t), t))
