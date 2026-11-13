import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); s = [(int(d[1+2*i]), int(d[2+2*i])) for i in range(n)]; best = 0
    for m in range(1 << n):
        c = [s[i] for i in range(n) if m >> i & 1]; c.sort()
        if all(c[i][1] <= c[i+1][0] for i in range(len(c)-1)): best = max(best, len(c))
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
