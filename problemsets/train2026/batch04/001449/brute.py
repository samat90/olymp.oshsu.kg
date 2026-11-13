import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import permutations
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n])); best = None
    for p in permutations(a):
        t = 0; w = 0
        for x in p: w += t; t += x
        best = w if best is None else min(best, w)
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
