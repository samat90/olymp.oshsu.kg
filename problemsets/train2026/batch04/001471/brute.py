import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, q = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); r = []
    for k in map(int, d[2+n:2+n+q]):
        c = 0; ans = -1
        for i in range(n):
            c += a[i]
            if c == k: ans = i+1; break
        r.append(ans)
    return ' '.join(map(str, r))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
