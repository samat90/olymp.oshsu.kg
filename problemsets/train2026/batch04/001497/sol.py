import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, B = int(d[0]), int(d[1]); c = 0
    for x in sorted(map(int, d[2:2+n])):
        if B >= x: B -= x; c += 1
        else: break
    return str(c)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
