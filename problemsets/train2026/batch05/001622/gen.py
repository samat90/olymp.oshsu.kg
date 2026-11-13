import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    L = sc(k, 200000); out = []; d = 0
    while len(out) < L:
        r = rng.random()
        if d and (len(out) + d >= L or r < 0.2): out.append(')'); d -= 1
        elif r < 0.4: out.append('('); d += 1
        else: out.append(rng.choice('abcdefgkoz'))
    out += [')'] * d
    return ''.join(out) + '\n'

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1622 * 100 + t), t))
