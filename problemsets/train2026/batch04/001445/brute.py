import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m = int(d[0]), int(d[1]); a = d[2:2+n]; b = d[2+n:2+n+m][:]; c = 0
    for x in a:
        if x in b: b.remove(x); c += 1
    return str(c)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
