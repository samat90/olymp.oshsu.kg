import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, K = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    return str(sum(1 for i in range(n) for j in range(i+1, n) if a[i]+a[j] == K))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
