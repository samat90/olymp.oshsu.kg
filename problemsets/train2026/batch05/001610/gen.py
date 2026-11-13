import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    q = sc(k, 200000); c = []; sz = 0; hi = rng.choice([3, 10**9])
    for _ in range(q):
        r = rng.random()
        if sz == 0 or r < 0.45: c.append('push %d' % rng.randint(-hi, hi)); sz += 1
        else:
            x = rng.choice(['pop', 'top', 'peekMax', 'popMax'])
            if x in ('pop', 'popMax'): sz -= 1
            c.append(x)
    return '%d\n%s\n' % (q, '\n'.join(c))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1610 * 100 + t), t))
