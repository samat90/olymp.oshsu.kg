import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n]))
    if n == 1: return '0'
    jumps = 0; end = 0; far = 0
    for i in range(n-1):
        far = max(far, i+a[i])
        if i == end:
            if far <= i: return '-1'
            jumps += 1; end = far
            if end >= n-1: break
    return str(jumps) if end >= n-1 else '-1'

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
