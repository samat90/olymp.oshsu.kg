import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split(); n, m = int(t[0]), int(t[1]); g = t[2:2 + n]
    best = 0
    for r1 in range(n):
        for r2 in range(r1, n):
            for c1 in range(m):
                for c2 in range(c1, m):
                    if all(g[r][c] == '1' for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)):
                        best = max(best, (r2 - r1 + 1) * (c2 - c1 + 1))
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
