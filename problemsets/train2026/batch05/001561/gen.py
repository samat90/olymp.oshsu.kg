import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 100000); m = rng.choice([1, 2, rng.randint(1, max(1, n // 3)), 5])
    t = sorted(rng.randint(0, rng.choice([20, 10**5, 10**9])) for _ in range(n))
    return '%d %d\n%s\n' % (n, m, '\n'.join('%d %d' % (x, rng.randint(1, rng.choice([5, 10**4]))) for x in t))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1561 * 100 + t), t))
