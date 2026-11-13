import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    q = sc(k, 3000); c = []; ln = 0; ops = 0
    for _ in range(q):
        r = rng.random()
        if r < 0.35:
            w = ''.join(rng.choice('abkoz') for _ in range(rng.randint(1, 5))); c.append('type ' + w); ln += len(w); ops += 1
        elif r < 0.5:
            d = rng.randint(0, ln); c.append('del %d' % d); ln -= d; ops += 1
        elif r < 0.7: c.append('undo')
        else: c.append('print')
    c[-1] = 'print'
    return '%d\n%s\n' % (q, '\n'.join(c))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1614 * 100 + t), t))
