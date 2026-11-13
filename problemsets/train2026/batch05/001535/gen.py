import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    L = sc(k, 100000)
    def ex(b, d):
        parts = []
        while b > 0:
            if d < 30 and b > 5 and rng.random() < 0.5:
                sub = rng.randint(1, max(1, b - 4))
                inner = ex(sub, d + 1)
                r = rng.randint(1, 99 if k > 3 else 4)
                parts.append('%d[%s]' % (r, inner)); b -= len(parts[-1])
            else:
                t = ''.join(rng.choice('abkoz') for _ in range(rng.randint(1, 4)))
                parts.append(t); b -= len(t)
        return ''.join(parts)
    r = ex(L, 0)
    return (r if r else 'a') + '\n'

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1535 * 100 + t), t))
