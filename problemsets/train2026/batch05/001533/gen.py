import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    m = sc(k, 100000)
    toks = []; depth = 0; pushes = 0
    while pushes < m + 1 or depth > 1:
        if pushes < m + 1 and (depth < 2 or rng.random() < 0.55):
            toks.append(str(rng.randint(0, 9))); depth += 1; pushes += 1
        else:
            toks.append(rng.choice('+-*')); depth -= 1
    return '%d\n%s\n' % (len(toks), ' '.join(toks))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1533 * 100 + t), t))
