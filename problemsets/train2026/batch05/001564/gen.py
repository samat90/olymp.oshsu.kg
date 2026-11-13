import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000)
    p = rng.choice([0.5, 0.2, 0.9])
    return '%d\n%s\n%s\n' % (n, ' '.join('1' if rng.random() < p else '0' for _ in range(n)), ' '.join('1' if rng.random() < 0.5 else '0' for _ in range(n)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1564 * 100 + t), t))
