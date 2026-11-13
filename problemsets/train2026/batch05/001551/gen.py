import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000)
    w = rng.choice([1, 2, rng.randint(1, n), n, max(1, n // 10)])
    w = min(max(w, 1), n)
    hi = rng.choice([3, 10**9])
    return '%d %d\n%s\n' % (n, w, ' '.join(str(rng.randint(-hi, hi)) for _ in range(n)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1551 * 100 + t), t))
