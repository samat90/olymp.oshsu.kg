import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = [(d[1+2*i], int(d[2+2*i])) for i in range(n)]
    for i in range(n):
        for j in range(n-1-i):
            x, y = a[j], a[j+1]
            if x[1] < y[1] or (x[1] == y[1] and x[0] > y[0]): a[j], a[j+1] = y, x
    return '\n'.join(x[0] for x in a)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
