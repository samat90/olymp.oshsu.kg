import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m = int(d[0]), int(d[1]); g = list(map(int, d[2:2+n])); s = list(map(int, d[2+n:2+n+m]))
    def rec(i, used):
        if i == n: return 0
        best = rec(i+1, used)
        for j in range(m):
            if not used >> j & 1 and s[j] >= g[i]: best = max(best, 1+rec(i+1, used | 1 << j))
        return best
    return str(rec(0, 0))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
