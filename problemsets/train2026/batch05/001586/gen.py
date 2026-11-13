import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); hi = 10**9 if k > 3 else 12
    if k > 3: hi = rng.choice([10**4, 10**9])
    c = [rng.randint(1, hi) for _ in range(n)]
    if sum(c) > 10**12: c = [x // 2 + 1 for x in c]
    return '%d %d\n%s\n' % (n, rng.randint(1, sum(c)), ' '.join(map(str, c)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1586 * 100 + t), t))
