import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, K = t[0], t[1]; c = t[2:2 + n]; rev = 0
    for _ in range(K):
        i = c.index(max(c)); rev += c[i]; c[i] -= 1
    return str(rev % MOD)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
