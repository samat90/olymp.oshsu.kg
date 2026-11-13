import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    L = sc(k, 200000) // 2 * 2 + 2
    mode = rng.randint(0, 2)
    out = []; d = 0
    while len(out) < L:
        if d and (len(out) + d >= L or rng.random() < (0.5 if mode else 0.2)):
            out.append(')'); d -= 1
        else:
            out.append('('); d += 1
    out += [')'] * d
    return ''.join(out) + '\n'

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1531 * 100 + t), t))
