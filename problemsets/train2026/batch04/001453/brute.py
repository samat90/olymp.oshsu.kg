import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n])); best = 0
    for i in range(n):
        for j in range(n):
            if a[i] < a[j] and not any(a[i] < x < a[j] for x in a): best = max(best, a[j]-a[i])
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
