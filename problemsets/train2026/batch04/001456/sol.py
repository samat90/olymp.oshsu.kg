import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, q = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); r = []
    for i in range(q):
        l, rr = int(d[2+n+2*i]), int(d[3+n+2*i]); r.append(bisect_right(a, rr)-bisect_left(a, l))
    return ' '.join(map(str, r))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
