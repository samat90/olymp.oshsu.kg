import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n*m])); q = int(d[2+n*m]); r = []
    for x in map(int, d[3+n*m:3+n*m+q]):
        lo, hi = 0, n*m-1; f = False
        while lo <= hi:
            mid = (lo+hi)//2; y = a[mid//m*m + mid % m]
            if y == x: f = True; break
            if y < x: lo = mid+1
            else: hi = mid-1
        r.append('YES' if f else 'NO')
    return '\n'.join(r)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
