import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    import heapq
    d = d.split(); n = int(d[0]); j = sorted((int(d[1+2*i]), int(d[2+2*i])) for i in range(n)); h = []
    for dl, p in j:
        heapq.heappush(h, p)
        if len(h) > dl: heapq.heappop(h)
    return str(sum(h))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
