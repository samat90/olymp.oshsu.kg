import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import permutations
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n])); b = list(map(int, d[1+n:1+2*n]))
    return str(max(sum(x*y for x, y in zip(a, p)) for p in permutations(b)))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
