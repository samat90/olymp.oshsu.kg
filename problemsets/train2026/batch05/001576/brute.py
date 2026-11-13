import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    L = s.strip().split('\n'); K, w = map(int, L[0].split()[:2])
    p = list(map(int, L[1].split())); c = list(map(int, L[2].split())); n = len(p)
    best = {0: w}; res = w
    for mask in range(1 << n):
        if mask not in best: continue
        cap = best[mask]; res = max(res, cap)
        if bin(mask).count('1') >= K: continue
        for i in range(n):
            if not mask >> i & 1 and c[i] <= cap:
                nm = mask | 1 << i
                best[nm] = max(best.get(nm, -1), cap + p[i])
    return str(res)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
