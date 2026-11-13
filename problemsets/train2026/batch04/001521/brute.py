import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, Ln = int(d[0]), int(d[1]); s = [(int(d[2+2*i]), int(d[3+2*i])) for i in range(n)]
    return str(sum(1 for x in range(Ln) if not any(l <= x < r for l, r in s)))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
