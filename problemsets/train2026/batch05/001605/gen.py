import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 100000)
    d = [rng.choice([0, 4, 5, 9, rng.randint(0, 9)]) for _ in range(n)]
    if n > 1 and d[0] == 0: d[0] = rng.randint(1, 9)
    return '%d\n%s\n' % (n, ' '.join(map(str, d)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1605 * 100 + t), t))
