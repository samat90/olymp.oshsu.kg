import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, T_ = int(d[0]), int(d[1]); s = sorted((int(d[2+2*i]), int(d[3+2*i])) for i in range(n)); cur = 0; best = 0
    for l, r in s:
        if l == r: continue
        best = max(best, l-cur); cur = max(cur, r)
    return str(max(best, T_-cur))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
