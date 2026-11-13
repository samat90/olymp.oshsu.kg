import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, b, l = t[:3]; h = t[3:3 + n]
    best = [1]
    def go(i, b, l):
        best[0] = max(best[0], i + 1)
        if i == n - 1: return
        d = h[i + 1] - h[i]
        if d <= 0: go(i + 1, b, l); return
        if b >= d: go(i + 1, b - d, l)
        if l > 0: go(i + 1, b, l - 1)
    go(0, b, l)
    return str(best[0])

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
