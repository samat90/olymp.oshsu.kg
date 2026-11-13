import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m = int(d[0]), int(d[1])
    A = [(int(d[2+2*i]), int(d[3+2*i])) for i in range(n)]; o = 2+2*n
    B = [(int(d[o+2*i]), int(d[o+1+2*i])) for i in range(m)]
    return str(sum(1 for a in A for b in B if a[0] <= b[1] and b[0] <= a[1]))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
