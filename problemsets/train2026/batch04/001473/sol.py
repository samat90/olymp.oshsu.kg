import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); t = []
    for x in map(int, d[1:1+n]):
        i = bisect_left(t, x)
        if i == len(t): t.append(x)
        else: t[i] = x
    return str(len(t))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
