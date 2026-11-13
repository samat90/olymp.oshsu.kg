import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = max(sc(k, 200000), 3); t = rng.choice([0, 1, rng.randint(0, n - 2)])
    la = rng.randint(1, n - 1 - t) if n - 1 - t >= 1 else 1
    t = min(t, n - 2)
    lb = n - la - t
    if lb < 1: lb = 1; la = n - t - 1
    ids = list(range(1, n + 1)); rng.shuffle(ids)
    A = ids[:la]; B = ids[la:la + lb]; T = ids[la + lb:]
    nxt = [0] * (n + 1)
    for ch in (A, B):
        for i in range(len(ch) - 1): nxt[ch[i]] = ch[i + 1]
    for i in range(len(T) - 1): nxt[T[i]] = T[i + 1]
    if T: nxt[A[-1]] = T[0]; nxt[B[-1]] = T[0]
    return '%d\n%s\n%d %d\n' % (n, ' '.join(map(str, nxt[1:])), A[0], B[0])

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1602 * 100 + t), t))
