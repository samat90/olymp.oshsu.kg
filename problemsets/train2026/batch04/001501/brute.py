import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import permutations
    d = d.split(); n = int(d[0]); j = [(int(d[1+2*i]), int(d[2+2*i])) for i in range(n)]; best = None
    for p in permutations(j):
        t = 0; r = 0
        for x, dl in p: t += x; r = max(r, t-dl)
        best = r if best is None else min(best, r)
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
