import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    import heapq
    d = d.split(); n = int(d[0]); h = list(map(int, d[1:1+n])); heapq.heapify(h); r = 0
    while len(h) > 1:
        x = heapq.heappop(h)+heapq.heappop(h); r += x; heapq.heappush(h, x)
    return str(r)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
