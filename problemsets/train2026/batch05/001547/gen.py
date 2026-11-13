import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000)
    d = rng.choice(['0123456789', '012', '19'])
    num = rng.choice('123456789') + ''.join(rng.choice(d) for _ in range(n - 1))
    return '%s\n%d\n' % (num, rng.randint(0, n))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1547 * 100 + t), t))
