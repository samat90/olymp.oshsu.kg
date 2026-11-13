import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split(); n, L = int(t[0]), int(t[1]); a = list(map(int, t[2:2 + n]))
    best = 0
    for i in range(n):
        for j in range(i, n):
            if max(a[i:j + 1]) - min(a[i:j + 1]) <= L: best = max(best, j - i + 1)
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
