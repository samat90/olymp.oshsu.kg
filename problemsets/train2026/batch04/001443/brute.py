import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); w = d[1:1+n]
    par = list(range(n))
    def f(x):
        while par[x] != x: x = par[x]
        return x
    for i in range(n):
        for j in range(i+1, n):
            if Counter(w[i]) == Counter(w[j]): par[f(i)] = f(j)
    return str(len({f(i) for i in range(n)}))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
