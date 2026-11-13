import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    s = s.split()[0]
    n = len(s); best = 0
    for i in range(n):
        b = 0
        for j in range(i, n):
            b += 1 if s[j] == '(' else -1
            if b < 0: break
            if b == 0: best = max(best, j - i + 1)
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
