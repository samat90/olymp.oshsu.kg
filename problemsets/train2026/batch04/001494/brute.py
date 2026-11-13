import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); q = int(d[0]); r = []
    for x in map(int, d[1:1+q]):
        dp = [0]+[10**9]*x
        for i in range(1, x+1):
            for k in (1, 5, 10, 50, 100, 500):
                if k <= i: dp[i] = min(dp[i], dp[i-k]+1)
        r.append(dp[x])
    return ' '.join(map(str, r))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
