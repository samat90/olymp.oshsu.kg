import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n = t[0]; nx = [0] + t[1:1 + n]; a, b = t[1 + n], t[2 + n]
    p, q = a, b
    while p != q:
        p = nx[p] if p else b
        q = nx[q] if q else a
    return str(p if p else -1)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
