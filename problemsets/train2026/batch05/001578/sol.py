import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, m, K = t[:3]; a = t[3:3 + n]; b = t[3 + n:3 + n + m]
    h = [(a[i] + b[0], i, 0) for i in range(min(n, K))]; heapq.heapify(h); res = []
    while h and len(res) < K:
        v, i, j = heapq.heappop(h); res.append(v)
        if j + 1 < m: heapq.heappush(h, (a[i] + b[j + 1], i, j + 1))
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
