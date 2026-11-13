import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); s = sorted((int(d[2+2*i]), int(d[1+2*i])) for i in range(n)); last = 0; c = 0
    for r, l in s:
        if l >= last: c += 1; last = r
    return str(c)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
