import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000)
    return '%d %d\n%s\n' % (n, rng.choice([0, rng.randint(0, 10**9), rng.randint(0, 2 * n)]), ' '.join(str(rng.randint(-10**9, 10**9)) for _ in range(n)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1596 * 100 + t), t))
