import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000); hi = rng.choice([3, 50, 10**9])
    a = [rng.randint(-hi, hi) for _ in range(n)]
    K = rng.randint(1, len(set(a)))
    return '%d %d\n%s\n' % (n, K, ' '.join(map(str, a)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1572 * 100 + t), t))
