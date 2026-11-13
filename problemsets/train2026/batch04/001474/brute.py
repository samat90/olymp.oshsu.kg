import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, q = int(d[0]), int(d[1]); s = [(int(d[2+2*i]), int(d[3+2*i])) for i in range(n)]
    return ' '.join(str(sum(1 for l, r in s if l <= x <= r)) for x in map(int, d[2+2*n:2+2*n+q]))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
