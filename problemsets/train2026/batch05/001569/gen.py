import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); K = rng.randint(1, min(n, rng.choice([1, 3, n])))
    hi = rng.choice([4, 10**9])
    return '%d %d\n%s\n' % (n, K, ' '.join(str(rng.randint(-hi, hi)) for _ in range(n)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1569 * 100 + t), t))
