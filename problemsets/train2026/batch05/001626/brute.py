import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, K = t[:2]; a = t[2:2 + n]
    dp = [0] * n
    for i in range(n):
        dp[i] = a[i] + max([0] + [dp[j] for j in range(max(0, i - K), i)])
    return str(max(dp))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
