import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, x = t[:2]; v = t[2:2 + n]
    lo = []; hi = []
    for y in v: (lo if y < x else hi).append(y)
    return ' '.join(map(str, lo + hi))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
