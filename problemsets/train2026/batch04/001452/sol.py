import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n]))
    o = sorted(x for x in a if x % 2); e = sorted((x for x in a if x % 2 == 0), reverse=True)
    return ' '.join(map(str, o + e))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
