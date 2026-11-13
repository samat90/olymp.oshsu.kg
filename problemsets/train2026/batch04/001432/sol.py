import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    import functools
    d = d.split(); n = int(d[0]); a = d[1:1+n]
    a.sort(key=functools.cmp_to_key(lambda x, y: -1 if x+y > y+x else (1 if x+y < y+x else 0)))
    r = ''.join(a)
    return '0' if set(r) == {'0'} else r

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
