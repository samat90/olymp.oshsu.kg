import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, K = t[0], t[1]; h = [-x for x in t[2:2 + n]]
    heapq.heapify(h)
    for _ in range(K):
        x = -h[0]; heapq.heapreplace(h, -math.isqrt(x))
    return str(-sum(h))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
