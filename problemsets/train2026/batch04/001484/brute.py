import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, V = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); H = min(a)
    while sum(max(0, H+1-x) for x in a) <= V: H += 1
    return str(H)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
