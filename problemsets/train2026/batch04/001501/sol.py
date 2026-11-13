import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); j = sorted((int(d[2+2*i]), int(d[1+2*i])) for i in range(n)); t = 0; r = 0
    for dl, x in j:
        t += x; r = max(r, t-dl)
    return str(r)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
