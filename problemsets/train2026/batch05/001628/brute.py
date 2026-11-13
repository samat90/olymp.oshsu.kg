import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    from itertools import permutations
    t = list(map(int, s.split())); n = t[0]; v = sorted(t[1:1 + n])
    for p in permutations(v):
        a = list(p); out = []
        while a:
            out.append(a.pop(0))
            if a: a.append(a.pop(0))
        if out == v: return ' '.join(map(str, p))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
