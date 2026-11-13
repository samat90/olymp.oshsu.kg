import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, q = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); r = []
    for x in map(int, d[2+n:2+n+q]):
        best = a[0]
        for y in a:
            if abs(y-x) < abs(best-x) or (abs(y-x) == abs(best-x) and y < best): best = y
        r.append(best)
    return ' '.join(map(str, r))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
