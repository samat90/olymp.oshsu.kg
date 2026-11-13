import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, b, l = t[:3]; h = t[3:3 + n]; hp = []
    for i in range(n - 1):
        d = h[i + 1] - h[i]
        if d <= 0: continue
        heapq.heappush(hp, d)
        if len(hp) > l:
            b -= heapq.heappop(hp)
            if b < 0: return str(i + 1)
    return str(n)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
