import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    s = d.strip(); res = ''
    while s:
        best = None
        for ch in set(s):
            k = (-s.count(ch), ch)
            if best is None or k < best: best = k
        ch = best[1]; res += ch*s.count(ch); s = s.replace(ch, '')
    return res

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
