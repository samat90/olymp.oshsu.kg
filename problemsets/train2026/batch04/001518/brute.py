import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    s = d.strip(); n = len(s); k = len(set(s)); best = None
    for m in range(1 << n):
        t = ''.join(s[i] for i in range(n) if m >> i & 1)
        if len(t) == k and len(set(t)) == k and (best is None or t < best): best = t
    return best

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
