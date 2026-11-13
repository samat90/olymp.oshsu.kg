import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n = t[0]; J = [(t[1 + 2 * i], t[2 + 2 * i]) for i in range(n)]
    best = 0
    for mask in range(1 << n):
        ds = sorted(J[i][0] for i in range(n) if mask >> i & 1)
        if all(d >= i + 1 for i, d in enumerate(ds)):
            best = max(best, sum(J[i][1] for i in range(n) if mask >> i & 1))
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
