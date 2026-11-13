import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); s = [(int(d[1+2*i]), int(d[2+2*i])) for i in range(n)]
    return str(max(sum(1 for l, r in s if l <= x <= r) for x in range(0, 10)))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
