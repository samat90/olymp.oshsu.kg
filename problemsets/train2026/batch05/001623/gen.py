import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    L = sc(k, 100000); els = ['H', 'O', 'Na', 'Cl', 'K', 'Mg', 'Ca', 'Fe', 'C', 'N', 'S']
    def f(b, d):
        out = []
        while b > 0:
            if d < 3 and b > 6 and rng.random() < 0.3:
                inner = f(rng.randint(1, max(1, b // 3)), d + 1)
                t = '(' + inner + ')' + (str(rng.randint(2, 4)) if rng.random() < 0.7 else '')
            else:
                t = rng.choice(els) + (str(rng.randint(2, 9)) if rng.random() < 0.4 else '')
            out.append(t); b -= len(t)
        return ''.join(out)
    return (f(L, 0) or 'H') + '\n'

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1623 * 100 + t), t))
