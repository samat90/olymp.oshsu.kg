import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m = int(d[0]), int(d[1]); best = -1; bi = 0
    for i in range(n):
        s = d[2+i]; lo, hi = 0, m
        while lo < hi:
            mid = (lo+hi)//2
            if s[mid] == '1': hi = mid
            else: lo = mid+1
        if m-lo > best: best = m-lo; bi = i+1
    return str(bi)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
