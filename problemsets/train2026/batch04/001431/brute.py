import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n]))
    res = []
    rest = a[:]
    while rest:
        best = None
        for x in set(rest):
            k = (-rest.count(x), x)
            if best is None or k < best: best = k
        x = best[1]; res += [x]*rest.count(x); rest = [y for y in rest if y != x]
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
