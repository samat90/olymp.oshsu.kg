import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); b = list(map(int, d[2+n:2+n+m]))
    return str(min(abs(x-y) for x in a for y in b))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
