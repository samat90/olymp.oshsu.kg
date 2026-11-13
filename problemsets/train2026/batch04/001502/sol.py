import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    import functools
    d = d.split(); n = int(d[0]); j = [(int(d[1+2*i]), int(d[2+2*i])) for i in range(n)]
    j.sort(key=functools.cmp_to_key(lambda a, b: a[0]*b[1]-b[0]*a[1]))
    t = 0; r = 0
    for x, w in j: t += x; r += t*w
    return str(r)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
