import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n = t[0]; a = t[1:1 + n]
    ids = list(range(n)); pos = 0; res = []
    while ids:
        i = ids.pop(pos); res.append(i + 1); v = a[i]
        m = len(ids)
        if m == 0: break
        pos = (pos + v - 1) % m if v > 0 else (pos + v) % m
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
