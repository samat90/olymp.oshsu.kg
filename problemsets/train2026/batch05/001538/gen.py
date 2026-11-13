import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    L = sc(k, 200000)
    K = rng.randint(2, 4)
    a = rng.choice(['ab', 'abc'])
    return '%d\n%s\n' % (K, ''.join(rng.choice(a) for _ in range(L)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1538 * 100 + t), t))
