import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, K = t[:2]; v = t[2:2 + n]
    sizes = [0] * K
    for i in range(n): sizes[i % K] += 1
    res = []; p = 0
    for L in sizes:
        res.append(' '.join(map(str, v[p:p + L])) or '-'); p += L
    return '\n'.join(res)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
