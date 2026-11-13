import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); t = 0
    while sum(t//x for x in a) < m: t += 1
    return str(t)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
