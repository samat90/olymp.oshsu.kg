import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, K = t[:2]; v = t[2:2 + n]
    q, r = divmod(n, K); res = []; p = 0
    for i in range(K):
        L = q + (1 if i < r else 0)
        res.append(' '.join(map(str, v[p:p + L])) or '-'); p += L
    return '\n'.join(res)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
