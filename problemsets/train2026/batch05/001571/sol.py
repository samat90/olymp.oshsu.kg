import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    lines = s.split('\n'); m = int(lines[0]); L = []
    for i in range(m):
        t = lines[1 + i].split(); L.append(list(map(int, t[1:])))
    h = [(L[i][0], i, 0) for i in range(m) if L[i]]
    heapq.heapify(h); res = []
    while h:
        v, i, j = heapq.heappop(h); res.append(v)
        if j + 1 < len(L[i]): heapq.heappush(h, (L[i][j + 1], i, j + 1))
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
