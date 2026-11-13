import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, S = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); p = [0]
    for x in a: p.append(p[-1]+x)
    best = 0
    for i in range(n):
        j = bisect_left(p, p[i]+S, i+1)
        if j <= n and (best == 0 or j-i < best): best = j-i
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
