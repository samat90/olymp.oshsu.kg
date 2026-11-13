import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, K = t[0], t[1]
    a = [t[2 + i * n:2 + (i + 1) * n] for i in range(n)]
    h = [(a[i][0], i, 0) for i in range(min(n, K))]; heapq.heapify(h)
    for _ in range(K):
        v, i, j = heapq.heappop(h)
        if j + 1 < n: heapq.heappush(h, (a[i][j + 1], i, j + 1))
    return str(v)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
