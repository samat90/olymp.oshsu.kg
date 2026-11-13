import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m, k = int(d[0]), int(d[1]), int(d[2]); a = list(map(int, d[3:3+n]))
    for t in range(1, max(a)+1):
        c = 0; i = 0
        while i+k <= n:
            if all(x <= t for x in a[i:i+k]): c += 1; i += k
            else: i += 1
        if c >= m: return str(t)
    return '-1'

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
