import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n = int(t[0]); h = [int(x) for x in t[1:1 + n]]
    heapq.heapify(h); tot = 0
    while len(h) > 1:
        a = heapq.heappop(h); b = heapq.heappop(h); tot += a + b; heapq.heappush(h, a + b)
    return str(tot)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
