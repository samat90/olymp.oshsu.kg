import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000)
    if k <= 3: n = min(n, 7)
    return '%d\n%s\n' % (n, ' '.join(map(str, rng.sample(range(1, 10**9), n))))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1628 * 100 + t), t))
