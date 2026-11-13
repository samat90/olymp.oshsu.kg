import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = sorted(map(int, d[1:1+n])); res = 0
    for k in range(n-1, 1, -1):
        i, j = 0, k-1
        while i < j:
            if a[i] + a[j] > a[k]: res += j - i; j -= 1
            else: i += 1
    return str(res)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
