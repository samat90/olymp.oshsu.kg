import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    n, k = map(int, s.split())
    d = deque(range(1, n + 1))
    while len(d) > 1:
        d.rotate(-((k - 1) % len(d)))
        d.popleft()
    return str(d[0])

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
