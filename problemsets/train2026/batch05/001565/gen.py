import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000)
    t = sorted(rng.randint(0, rng.choice([10, 1000, 10**9])) for _ in range(n))
    return '%d %d\n%s\n' % (n, rng.choice([0, 1, 3, 100, 10**6, 10**9]), ' '.join(map(str, t)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1565 * 100 + t), t))
