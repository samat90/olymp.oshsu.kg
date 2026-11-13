import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n = t[0]; nx = [0] + t[1:1 + n]; a, b = t[1 + n], t[2 + n]
    seen = set(); c = a
    while c: seen.add(c); c = nx[c]
    c = b
    while c:
        if c in seen: return str(c)
        c = nx[c]
    return '-1'

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
