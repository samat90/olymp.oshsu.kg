import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, q = int(d[0]), int(d[1]); w = sorted(d[2:2+n])
    return ' '.join(str(bisect_left(w, p+'{')-bisect_left(w, p)) for p in d[2+n:2+n+q])

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
