import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); p = list(map(int, d[1:1+n])); best = 0
    for mask in range(1 << (n-1)):
        cuts = [0] + [i+1 for i in range(n-1) if mask >> i & 1] + [n]
        r = []
        for x, y in zip(cuts, cuts[1:]): r += sorted(p[x:y])
        if r == sorted(p): best = max(best, len(cuts)-1)
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
