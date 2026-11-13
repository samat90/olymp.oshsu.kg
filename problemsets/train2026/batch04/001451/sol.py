import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    c = Counter(d.strip()); return ''.join(ch*k for ch, k in sorted(c.items(), key=lambda x: (-x[1], x[0])))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
