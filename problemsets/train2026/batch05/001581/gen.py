import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); A = rng.choice([5, 10**4, 10**9])
    return '%d\n%s\n' % (n, '\n'.join('%d %d' % (rng.randint(1, A), rng.randint(1, rng.choice([4, A]))) for _ in range(n)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1581 * 100 + t), t))
