import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n = t[0]
    iv = sorted((t[1 + 2 * i], t[2 + 2 * i]) for i in range(n)); h = []
    for a, b in iv:
        if h and h[0] <= a: heapq.heapreplace(h, b)
        else: heapq.heappush(h, b)
    return str(len(h))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
