import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, S = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); best = 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += a[j]
            if s >= S:
                if best == 0 or j-i+1 < best: best = j-i+1
                break
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
