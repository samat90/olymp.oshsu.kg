import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    q = sc(k, 200000); cap = rng.randint(1, max(1, q // rng.choice([1, 3, 20])))
    c = []
    for _ in range(q):
        r = rng.random()
        if r < 0.45: c.append('push %d' % rng.randint(-10**9, 10**9))
        elif r < 0.75: c.append('pop')
        else: c.append('inc %d %d' % (rng.randint(1, cap + 2), rng.randint(-10**3, 10**3)))
    return '%d %d\n%s\n' % (cap, q, '\n'.join(c))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1611 * 100 + t), t))
