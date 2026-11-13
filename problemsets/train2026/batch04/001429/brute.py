import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n]))
    for i in range(n):
        for j in range(n-1-i):
            x, y = a[j], a[j+1]
            if (x % 10, x) > (y % 10, y): a[j], a[j+1] = y, x
    return ' '.join(map(str, a))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
