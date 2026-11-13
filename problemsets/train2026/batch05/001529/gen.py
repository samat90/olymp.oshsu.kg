import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    L = sc(k, 100000)
    pairs = ['()', '[]', '{}']
    st = []; out = []
    while len(out) < L:
        if st and (rng.random() < 0.5 or len(out) + len(st) >= L):
            out.append(st.pop()[1])
        else:
            p = rng.choice(pairs); st.append(p); out.append(p[0])
    while st: out.append(st.pop()[1])
    if rng.random() < 0.5:
        i = rng.randrange(len(out)); out[i] = rng.choice('()[]{}')
    return ''.join(out) + '\n'

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1529 * 100 + t), t))
