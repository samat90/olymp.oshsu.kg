import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); R = rng.choice([2, 10**4])
    return '%d %d\n%s\n' % (n, rng.randint(1, n), '\n'.join('%d %d' % (rng.randint(-R, R), rng.randint(-R, R)) for _ in range(n)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1584 * 100 + t), t))
