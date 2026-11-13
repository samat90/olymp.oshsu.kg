import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); s = sorted((int(d[1+2*i]), int(d[2+2*i])) for i in range(n)); c = 0; tot = 0
    cl, cr = s[0]
    for l, r in s[1:]:
        if l <= cr: cr = max(cr, r)
        else: c += 1; tot += cr-cl; cl, cr = l, r
    c += 1; tot += cr-cl
    return f"{c} {tot}"

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
