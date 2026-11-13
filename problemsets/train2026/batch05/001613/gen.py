import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    q = sc(k, 200000); names = ['osh', 'naryn', 'talas', 'karakol', 'batken', 'jalalabad', 'bishkek', 'toktogul']
    c = []
    for _ in range(q):
        r = rng.random()
        if r < 0.4: c.append('visit ' + rng.choice(names))
        else: c.append('%s %d' % (rng.choice(['back', 'forward']), rng.choice([1, 2, 5, rng.randint(1, 10**9)])))
    return '%s\n%d\n%s\n' % (rng.choice(names), q, '\n'.join(c))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1613 * 100 + t), t))
