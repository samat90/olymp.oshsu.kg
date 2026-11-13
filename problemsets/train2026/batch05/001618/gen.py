import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); hi = rng.choice([3, 10**9]); p = rng.choice([0.3, 0.5, 0.7])
    return '%d\n%s\n' % (n, ' '.join(str(rng.randint(1, hi) * (1 if rng.random() < p else -1)) for _ in range(n)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1618 * 100 + t), t))
