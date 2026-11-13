import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n]))
    r = {v: i+1 for i, v in enumerate(sorted(set(a)))}
    return ' '.join(str(r[x]) for x in a)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
