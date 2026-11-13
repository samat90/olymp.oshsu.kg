import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n]))
    for i in range(n):
        if k and a[i] < 0: a[i] = -a[i]; k -= 1
    s = sum(a)
    if k % 2: s -= 2*min(a)
    return str(s)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
