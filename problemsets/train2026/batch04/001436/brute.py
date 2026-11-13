import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    u = []
    for x in a:
        if x not in u: u.append(x)
    for i in range(len(u)):
        for j in range(len(u)-1-i):
            if u[j] > u[j+1]: u[j], u[j+1] = u[j+1], u[j]
    return str(u[k-1]) if k <= len(u) else '-1'

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
