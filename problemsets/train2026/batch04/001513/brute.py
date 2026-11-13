import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = tuple(map(int, d[1:1+n])); memo = {}
    def rec(t):
        if len(t) == 1: return 0
        if t in memo: return memo[t]
        best = None
        for i in range(len(t)):
            for j in range(i+1, len(t)):
                nt = tuple(sorted([t[k] for k in range(len(t)) if k != i and k != j] + [t[i]+t[j]]))
                r = t[i]+t[j]+rec(nt); best = r if best is None else min(best, r)
        memo[t] = best; return best
    return str(rec(tuple(sorted(a))))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
