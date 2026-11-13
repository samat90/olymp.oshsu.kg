import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, q = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); p = []; s = 0
    for x in a: s += x; p.append(s)
    r = []
    for x in map(int, d[2+n:2+n+q]):
        i = bisect_left(p, x); r.append(i+1 if i < n else -1)
    return ' '.join(map(str, r))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
