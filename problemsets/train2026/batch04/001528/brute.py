import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); s = [(int(d[2+2*i]), int(d[3+2*i])) for i in range(n)]; x = 0
    while k:
        x += 1
        if not any(l <= x <= r for l, r in s): k -= 1
    return str(x)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
