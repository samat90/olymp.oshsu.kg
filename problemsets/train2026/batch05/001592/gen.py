import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000)
    order = list(range(2, n + 1)); rng.shuffle(order); order = [1] + order
    nxt = [0] * (n + 1)
    for i in range(n - 1): nxt[order[i]] = order[i + 1]
    nxt[order[-1]] = rng.choice([0, order[rng.randrange(n)]])
    return '%d\n%s\n' % (n, ' '.join(map(str, nxt[1:])))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1592 * 100 + t), t))
