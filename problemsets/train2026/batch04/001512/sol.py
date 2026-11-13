import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n]))
    up = down = 1
    for i in range(1, n):
        if a[i] > a[i-1]: up = down+1
        elif a[i] < a[i-1]: down = up+1
    return str(max(up, down))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
