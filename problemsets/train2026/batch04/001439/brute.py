import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n])); b = sorted(a)
    best = 0 if a == b else None
    if best is None:
        for ln in range(1, n+1):
            for l in range(n-ln+1):
                c = a[:l] + sorted(a[l:l+ln]) + a[l+ln:]
                if c == b: return str(ln)
    return '0'

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
