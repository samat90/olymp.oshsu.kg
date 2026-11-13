import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); B = int(d[0]); c = list(map(int, d[1:10])); m = min(c)
    if B < m: return '-1'
    n = B//m; res = []
    for i in range(n):
        for dg in range(9, 0, -1):
            if B-c[dg-1] >= (n-i-1)*m: res.append(str(dg)); B -= c[dg-1]; break
    return ''.join(res)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
