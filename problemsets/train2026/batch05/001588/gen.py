import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); a = rng.choice(['AB', 'ABC', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'])
    if k <= 3: n = min(n, 6); a = a[:3]
    return '%s\n%d\n' % (''.join(rng.choice(a) for _ in range(n)), rng.randint(0, 2 if k <= 3 else 100))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1588 * 100 + t), t))
