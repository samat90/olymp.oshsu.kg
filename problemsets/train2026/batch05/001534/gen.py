import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    L = sc(k, 100000)
    def ex(b, d):
        out = []; first = True
        while True:
            if not first: out.append(rng.choice('+-*'))
            first = False
            if d < 25 and b > 8 and rng.random() < 0.3:
                sub = rng.randint(1, b // 2); out.append('(' + ex(sub, d + 1) + ')'); b -= sub + 2
            else:
                t = str(rng.randint(0, 9) if rng.random() < 0.6 else rng.randint(10, 10 ** 9)); out.append(t); b -= len(t)
            b -= 1
            if b <= 0: break
        return ''.join(out)
    res = ex(L, 0)
    return res + '\n'

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1534 * 100 + t), t))
