import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    L = sc(k, 100000)
    names = ['ala', 'too', 'sary', 'osh', 'kg', 'a', 'b', '..', '..', '.', '']
    out = '/'
    while len(out) < L:
        out += rng.choice(names) + rng.choice(['/', '/', '//'])
    if rng.random() < 0.5: out = out.rstrip('/') or '/'
    return out + '\n'

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1536 * 100 + t), t))
