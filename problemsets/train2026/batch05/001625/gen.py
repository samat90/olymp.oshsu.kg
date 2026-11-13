import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); hi = rng.choice([5, 10**5])
    return '%d %d\n%s\n' % (n, rng.randint(1, hi * rng.choice([1, 3, 20])), ' '.join(str(rng.randint(-hi, hi)) for _ in range(n)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1625 * 100 + t), t))
