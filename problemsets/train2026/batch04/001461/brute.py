import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m = int(d[0]), int(d[1]); c = [d[2+i].count('1') for i in range(n)]
    return str(c.index(max(c))+1)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
