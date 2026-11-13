import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, X = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    return str(min((abs(a[i]+a[j]-X), a[i]+a[j]) for i in range(n) for j in range(i+1, n))[1])

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
