import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n])); b = a[:]
    for i in range(n):
        for j in range(n-1-i):
            if b[j] > b[j+1]: b[j], b[j+1] = b[j+1], b[j]
    c = 0
    for i in range(n):
        if a[i] != b[i]: c += 1
    return str(c)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
