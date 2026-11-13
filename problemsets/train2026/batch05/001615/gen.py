import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    q = sc(k, 200000); hi = rng.choice([2, 5, 10**9]); c = []; sz = 0
    for _ in range(q):
        if sz == 0 or rng.random() < 0.55: c.append('push %d' % rng.randint(0, hi)); sz += 1
        else: c.append('pop'); sz -= 1
    if 'pop' not in c: c[-2:] = ['push 1', 'pop']
    return '%d\n%s\n' % (q, '\n'.join(c))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1615 * 100 + t), t))
