import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    q = sc(k, 200000); c = []; sz = 0
    for _ in range(q):
        r = rng.random()
        if sz == 0 or r < 0.45: c.append('push %d' % rng.randint(-10**9, 10**9)); sz += 1
        elif r < 0.65: c.append('pop'); sz -= 1
        else: c.append(rng.choice(['top', 'min']))
    return '%d\n%s\n' % (q, '\n'.join(c))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1609 * 100 + t), t))
