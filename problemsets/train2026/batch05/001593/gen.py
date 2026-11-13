import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); m = sc(k, 200000); hi = rng.choice([4, 10**9])
    a = sorted(rng.randint(-hi, hi) for _ in range(n)); b = sorted(rng.randint(-hi, hi) for _ in range(m))
    return '%d %d\n%s\n%s\n' % (n, m, ' '.join(map(str, a)), ' '.join(map(str, b)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1593 * 100 + t), t))
