import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 1000)
    return '%d %d\n%s\n' % (n, rng.choice([1, 3, 10, 100, 1000]), ' '.join(str(rng.randint(1, rng.choice([5, 1000]))) for _ in range(n)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1562 * 100 + t), t))
