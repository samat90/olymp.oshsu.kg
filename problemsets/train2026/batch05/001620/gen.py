import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); r = []; sz = 0
    for _ in range(n):
        x = rng.random()
        if sz >= 2 and x < 0.2: r.append('+'); sz += 1
        elif sz >= 1 and x < 0.4: r.append('D'); sz += 1
        elif sz >= 1 and x < 0.55: r.append('C'); sz -= 1
        else: r.append(str(rng.randint(-30000, 30000))); sz += 1
    return '%d\n%s\n' % (n, ' '.join(r))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1620 * 100 + t), t))
