import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import combinations
    d = d.split(); n, k = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n]))
    return str(max(min(c[i+1]-c[i] for i in range(k-1)) for c in combinations(a, k)))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
