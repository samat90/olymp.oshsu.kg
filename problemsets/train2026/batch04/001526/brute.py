import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, T_ = int(d[0]), int(d[1]); s = [(int(d[2+2*i]), int(d[3+2*i])) for i in range(n)]
    free = [not any(l <= x < r for l, r in s) for x in range(T_)]; best = cur = 0
    for f in free:
        cur = cur+1 if f else 0; best = max(best, cur)
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
