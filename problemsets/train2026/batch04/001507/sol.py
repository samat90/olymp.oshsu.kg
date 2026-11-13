import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    if n % k: return 'NO'
    c = Counter(a)
    for x in sorted(c):
        t = c[x]
        if t:
            for y in range(x, x+k):
                if c.get(y, 0) < t: return 'NO'
                c[y] -= t
    return 'YES'

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
