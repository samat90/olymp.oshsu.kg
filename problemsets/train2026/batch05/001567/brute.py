import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n = t[0]; a = t[1:1 + n]
    nx = [(i + 1) % n for i in range(n)]; pv = [(i - 1) % n for i in range(n)]
    cur = 0; res = []
    for r in range(n):
        res.append(cur + 1); v = a[cur]
        if r == n - 1: break
        p, q = pv[cur], nx[cur]
        nx[p] = q; pv[q] = p
        left = n - 1 - r
        if v > 0:
            x = q
            for _ in range((v - 1) % left): x = nx[x]
        else:
            x = p
            for _ in range((-v - 1) % left): x = pv[x]
        cur = x
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
