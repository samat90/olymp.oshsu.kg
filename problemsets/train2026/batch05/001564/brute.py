import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split(); n = int(t[0]); d = deque(t[1:1 + n]); b = deque(t[1 + n:1 + 2 * n])
    fails = 0
    while d and b and fails < len(d):
        if d[0] == b[0]: d.popleft(); b.popleft(); fails = 0
        else: d.rotate(-1); fails += 1
    return str(len(d))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
