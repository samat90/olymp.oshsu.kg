import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    import heapq
    d = d.split(); n, k = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    if k > n: return '0'
    h = [-x for x in a]; heapq.heapify(h); c = 0
    while len(h) >= k and -h[0] > 0:
        t = [heapq.heappop(h) for _ in range(k)]
        if t[-1] == 0: break
        for x in t:
            if x+1 < 0: heapq.heappush(h, x+1)
        c += 1
        if c > 10**6: break
    return str(c)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
