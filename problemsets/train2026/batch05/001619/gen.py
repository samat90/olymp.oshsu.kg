import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 200000)
    if k <= 3: n = min(n, 8)
    if rng.random() < 0.5:
        res = []; st = []; nxt = 1
        while len(res) < n:
            if nxt <= n and (not st or rng.random() < 0.5): st.append(nxt); nxt += 1
            else: res.append(st.pop())
    else:
        res = list(range(1, n + 1)); rng.shuffle(res)
    return '%d\n%s\n' % (n, ' '.join(map(str, res)))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1619 * 100 + t), t))
