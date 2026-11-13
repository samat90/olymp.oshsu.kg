import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000)
    if k <= 3: n = min(n, 9)
    hi = rng.choice([5, 10**9])
    return '%d %d %d\n%s\n' % (n, rng.randint(0, hi), rng.randint(0, min(n, 4)), ' '.join(str(rng.randint(1, hi)) for _ in range(n)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1627 * 100 + t), t))
