import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    L = sc(k, 200000)
    return '%d %d %d\n%s\n' % (L, rng.randint(1, max(1, L // 3 + 1)), rng.randint(1, max(1, L // 3 + 1)), ' '.join(str(rng.randint(-10**9, 10**9)) for _ in range(L)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1607 * 100 + t), t))
