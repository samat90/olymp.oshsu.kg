import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    q = sc(k, 200000); cap = rng.randint(1, max(1, min(q, 5 if k <= 4 else 1000)))
    K = rng.randint(1, cap * 2 + 1)
    c = []
    for _ in range(q):
        if rng.random() < 0.5: c.append('put %d %d' % (rng.randint(0, K), rng.randint(0, 10**9)))
        else: c.append('get %d' % rng.randint(0, K))
    c[-1] = 'get %d' % rng.randint(0, K)
    return '%d %d\n%s\n' % (cap, q, '\n'.join(c))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1612 * 100 + t), t))
