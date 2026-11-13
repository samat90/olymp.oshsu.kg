import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n])); b = sorted(a)
    l = 0
    while l < n and a[l] == b[l]: l += 1
    if l == n: return '0'
    r = n-1
    while a[r] == b[r]: r -= 1
    return str(r-l+1)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
