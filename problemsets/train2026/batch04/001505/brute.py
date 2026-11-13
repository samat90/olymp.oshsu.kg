import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import combinations
    s, k = d.split(); k = int(k); n = len(s)
    return str(min(int(''.join(s[i] for i in c)) for c in combinations(range(n), n-k)))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
