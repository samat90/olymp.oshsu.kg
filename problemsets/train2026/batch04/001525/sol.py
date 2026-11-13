import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); s = sorted((int(d[1+2*i]), int(d[2+2*i])) for i in range(n))
    return 'YES' if all(s[i][1] <= s[i+1][0] for i in range(n-1)) else 'NO'

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
