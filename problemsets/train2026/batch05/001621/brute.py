import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    s = s.split()[0]
    sys.setrecursionlimit(10000)
    def f(i):
        tot = 0
        while i < len(s) and s[i] == '(':
            if s[i + 1] == ')': tot += 1; i += 2
            else:
                v, i = f(i + 1); tot += 2 * v; i += 1
        return tot, i
    return str(f(0)[0] % MOD)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
