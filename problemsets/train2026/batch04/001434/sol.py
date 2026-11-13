import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, K = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n]))
    i, j, res = 0, n-1, 0
    while i < j:
        if a[i] + a[j] <= K: res += j - i; i += 1
        else: j -= 1
    return str(res)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
