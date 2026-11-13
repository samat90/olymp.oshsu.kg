import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = d[1:1+n]
    def less(x, y):
        if len(x) != len(y): return len(x) < len(y)
        return x < y
    for i in range(n):
        for j in range(n-1-i):
            if less(a[j+1], a[j]): a[j], a[j+1] = a[j+1], a[j]
    return '\n'.join(a)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
