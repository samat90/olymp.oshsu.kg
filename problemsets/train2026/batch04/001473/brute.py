import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n])); dp = [1]*n
    for i in range(n):
        for j in range(i):
            if a[j] < a[i]: dp[i] = max(dp[i], dp[j]+1)
    return str(max(dp))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
