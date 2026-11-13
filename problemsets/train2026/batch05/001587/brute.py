import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, K = t[0], t[1]
    memo = {}
    def f(a, k):
        if k == 0: return sum(a)
        key = (tuple(sorted(a)), k)
        if key in memo: return memo[key]
        r = max(f(a[:i] + [-a[i]] + a[i + 1:], k - 1) for i in range(len(a)))
        memo[key] = r
        return r
    return str(f(t[2:2 + n], K))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
