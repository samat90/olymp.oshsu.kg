import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import combinations
    d = d.split(); n, Ln = int(d[0]), int(d[1]); s = [(int(d[2+2*i]), int(d[3+2*i])) for i in range(n)]
    for k in range(1, n+1):
        for c in combinations(s, k):
            cur = 0
            for l, r in sorted(c):
                if l > cur: break
                cur = max(cur, r)
            if cur >= Ln: return str(k)
    return '-1'

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
