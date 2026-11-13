import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); q = int(d[0]); r = []
    for k in map(int, d[1:1+q]):
        n = 0; f = 1
        while True:
            s = str(f); z = len(s)-len(s.rstrip('0'))
            if z >= k: break
            n += 1; f *= n
        r.append(n)
    return ' '.join(map(str, r))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
