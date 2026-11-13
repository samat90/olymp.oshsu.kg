import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); st_ = sorted(int(d[1+2*i]) for i in range(n)); en = sorted(int(d[2+2*i]) for i in range(n))
    j = 0; best = 0
    for i in range(n):
        while en[j] <= st_[i]: j += 1
        best = max(best, i-j+1)
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
