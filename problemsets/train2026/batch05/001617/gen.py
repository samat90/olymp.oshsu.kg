import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    m = max(2, sc(k, 200000) // 2 * 2); n = rng.randint(1, min(1000, m // 2 + 1)); big = k > 4
    ev = []; st = []; lo = 0; starts = m // 2; used = 0
    while len(ev) < m:
        if st and (used == starts or rng.random() < 0.5):
            f, s0 = st.pop(); t = lo + rng.randint(0, 2 if not big else 1000); t = max(t, s0)
            ev.append((f, 'end', t)); lo = t + 1
        else:
            f = rng.randrange(n); t = lo + rng.randint(0, 2 if not big else 1000)
            ev.append((f, 'start', t)); st.append((f, t)); lo = t; used += 1
    return '%d %d\n%s\n' % (n, m, '\n'.join('%d %s %d' % e for e in ev))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1617 * 100 + t), t))
