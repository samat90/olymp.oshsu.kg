import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, Ln = int(d[0]), int(d[1]); p = list(map(int, d[2:2+n]))
    r = 0
    while True:
        cur = 0; ok = True
        for l, rr in sorted((x-r, x+r) for x in p):
            if l > cur: ok = False; break
            cur = max(cur, rr)
        if ok and cur >= Ln: return str(r)
        r += 1

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
