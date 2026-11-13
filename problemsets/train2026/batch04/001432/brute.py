import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import permutations
    d = d.split(); n = int(d[0]); a = d[1:1+n]
    r = max(''.join(p) for p in permutations(a))
    return '0' if set(r) == {'0'} else r

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
