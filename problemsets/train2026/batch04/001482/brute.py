import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, h = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    v = 1
    while sum(-(-x//v) for x in a) > h: v += 1
    return str(v)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
