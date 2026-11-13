import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n]))
    r = {v: i+1 for i, v in enumerate(sorted(set(a)))}; m = len(r)
    t = [0]*(m+1); res = 0
    for i, x in enumerate(a):
        k = r[x]; c = 0
        while k > 0: c += t[k]; k -= k & -k
        res += i - c
        k = r[x]
        while k <= m: t[k] += 1; k += k & -k
    return str(res)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
