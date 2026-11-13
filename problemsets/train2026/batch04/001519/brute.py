import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); s = [(int(d[1+2*i]), int(d[2+2*i])) for i in range(n)]
    par = list(range(n))
    def f(x):
        while par[x] != x: x = par[x]
        return x
    for i in range(n):
        for j in range(i+1, n):
            if s[i][0] <= s[j][1] and s[j][0] <= s[i][1]: par[f(i)] = f(j)
    cells = set()
    for l, r in s:
        for x in range(l, r): cells.add(x)
    return f"{len({f(i) for i in range(n)})} {len(cells)}"

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
