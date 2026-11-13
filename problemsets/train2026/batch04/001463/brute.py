import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n*m])); q = int(d[2+n*m])
    return '\n'.join('YES' if any(y == x for y in a) else 'NO' for x in map(int, d[3+n*m:3+n*m+q]))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
