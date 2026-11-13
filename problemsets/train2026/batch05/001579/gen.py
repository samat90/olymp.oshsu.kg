import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); T = rng.choice([10, 1000, 10**9]); r = []
    for _ in range(n):
        a = rng.randint(0, T - 1); b = rng.randint(a + 1, min(T, a + rng.choice([2, T])))
        r.append('%d %d' % (a, b))
    return '%d\n%s\n' % (n, '\n'.join(r))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1579 * 100 + t), t))
