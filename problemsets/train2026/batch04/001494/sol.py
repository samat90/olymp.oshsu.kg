import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); q = int(d[0]); r = []
    for x in map(int, d[1:1+q]):
        c = 0
        for k in (500, 100, 50, 10, 5, 1): c += x//k; x %= k
        r.append(c)
    return ' '.join(map(str, r))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
