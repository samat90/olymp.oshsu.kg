import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, K = t[:2]; a = t[2:2 + n]; best = -1
    for i in range(n):
        tot = 0
        for j in range(i, n):
            tot += a[j]
            if tot >= K:
                if best == -1 or j - i + 1 < best: best = j - i + 1
                break
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
