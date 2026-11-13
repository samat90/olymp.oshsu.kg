import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); hi = rng.choice([3, 10**9])
    K = rng.randint(1, 4) if k <= 3 else rng.randint(1, 2 * n)
    return '%d %d\n%s\n' % (n, K, ' '.join(str(rng.randint(-hi, hi)) for _ in range(n)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1587 * 100 + t), t))
