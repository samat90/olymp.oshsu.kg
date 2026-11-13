import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); B = int(d[0]); c = list(map(int, d[1:10]))
    best = [''] * (B+1)
    for b in range(1, B+1):
        cur = best[b-1]
        for dg in range(1, 10):
            if c[dg-1] <= b:
                cand = str(dg) + best[b-c[dg-1]] if True else ''
                cand2 = best[b-c[dg-1]] + str(dg)
                for x in (cand, cand2):
                    if (len(x), x) > (len(cur), cur): cur = x
        best[b] = cur
    return best[B] or '-1'

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
