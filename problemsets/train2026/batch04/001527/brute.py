import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); s = [(int(d[1+2*i]), int(d[2+2*i])) for i in range(n)]
    return str(sum(1 for i in range(n) if any(j != i and s[j][0] <= s[i][0] and s[i][1] <= s[j][1] for j in range(n))))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
