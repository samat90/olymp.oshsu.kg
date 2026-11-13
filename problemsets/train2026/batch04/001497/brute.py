import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, B = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    return str(max(bin(m).count('1') for m in range(1 << n) if sum(a[i] for i in range(n) if m >> i & 1) <= B))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
