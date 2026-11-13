import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = [(d[1+2*i], int(d[2+2*i])) for i in range(n)]
    a.sort(key=lambda x: (-x[1], x[0])); return '\n'.join(x[0] for x in a)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
