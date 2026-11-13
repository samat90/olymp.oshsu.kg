import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); g = list(map(int, d[1:1+n])); c = list(map(int, d[1+n:1+2*n]))
    for s in range(n):
        t = 0; ok = True
        for k in range(n):
            i = (s+k) % n; t += g[i]-c[i]
            if t < 0: ok = False; break
        if ok: return str(s+1)
    return '-1'

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
