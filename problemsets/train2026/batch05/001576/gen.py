import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); hi = rng.choice([5, 10**9])
    return '%d %d %d\n%s\n%s\n' % (rng.randint(1, n), rng.randint(0, hi // 2), n, ' '.join(str(rng.randint(0, hi)) for _ in range(n)), ' '.join(str(rng.randint(0, hi)) for _ in range(n)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1576 * 100 + t), t))
