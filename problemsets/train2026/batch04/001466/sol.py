import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n]))
    return str(sum(1 for x in a if (lambda i: i < n and a[i] == x+k)(bisect_left(a, x+k))))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
