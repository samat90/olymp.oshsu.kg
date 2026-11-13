import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    q = sc(k, 200000); names = ['Aigul', 'Bakyt', 'Cholpon', 'Dastan', 'Emil', 'Nurzat', 'Ulan']; hi = rng.choice([3, 10**9]); c = []
    for _ in range(q):
        if rng.random() < 0.55: c.append('come %s %d' % (rng.choice(names), rng.randint(1, hi)))
        else: c.append('next')
    return '%d\n%s\n' % (q, '\n'.join(c))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1616 * 100 + t), t))
