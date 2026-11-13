import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import combinations
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n]))
    return str(max(x*y*z for x, y, z in combinations(a, 3)))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
