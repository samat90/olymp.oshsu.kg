import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import combinations
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n])); c = 0
    for x, y, z in combinations(a, 3):
        s = sorted((x, y, z))
        if s[0] + s[1] > s[2]: c += 1
    return str(c)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
