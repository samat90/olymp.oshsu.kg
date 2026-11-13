import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); q = int(d[0]); r = []
    for i in range(q):
        a, b, h = int(d[1+3*i]), int(d[2+3*i]), int(d[3+3*i]); x = 0; day = 0
        while True:
            day += 1; x += a
            if x >= h: break
            x -= b
        r.append(day)
    return ' '.join(map(str, r))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
