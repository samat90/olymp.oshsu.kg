import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n]))
    hold = -a[0]; free = 0
    for x in a[1:]:
        free, hold = max(free, hold+x), max(hold, free-x)
    return str(free)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
