import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    L = s.strip().split('\n'); K, w = map(int, L[0].split()[:2])
    p = list(map(int, L[1].split())); c = list(map(int, L[2].split()))
    pr = sorted(zip(c, p)); h = []; i = 0
    for _ in range(K):
        while i < len(pr) and pr[i][0] <= w:
            heapq.heappush(h, -pr[i][1]); i += 1
        if not h: break
        w -= heapq.heappop(h)
    return str(w)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
