import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 700); m = sc(k, 700)
    if k > 2: m = max(3, m - rng.randint(0, m // 3))
    p = rng.choice([0.5, 0.8, 0.95])
    return '%d %d\n%s\n' % (n, m, '\n'.join(''.join('1' if rng.random() < p else '0' for _ in range(m)) for _ in range(n)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1543 * 100 + t), t))
