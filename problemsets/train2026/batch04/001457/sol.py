import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, q = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); r = []
    for x in map(int, d[2+n:2+n+q]):
        i = bisect_left(a, x); c = []
        if i < n: c.append(a[i])
        if i > 0: c.append(a[i-1])
        r.append(min(c, key=lambda y: (abs(y-x), y)))
    return ' '.join(map(str, r))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
