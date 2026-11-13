import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 100000); m = sc(k, 100000)
    def num(L):
        d = [rng.choice([0, 9, rng.randint(0, 9)]) for _ in range(L)]
        if L > 1 and d[-1] == 0: d[-1] = rng.randint(1, 9)
        return d
    a = num(n); b = num(m)
    return '%d %d\n%s\n%s\n' % (n, m, ' '.join(map(str, a)), ' '.join(map(str, b)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1600 * 100 + t), t))
