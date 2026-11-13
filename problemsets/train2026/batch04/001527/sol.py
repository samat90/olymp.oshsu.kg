import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); s = [(int(d[1+2*i]), int(d[2+2*i])) for i in range(n)]
    cnt = Counter(s); order = sorted(set(s), key=lambda x: (x[0], -x[1])); mx = -1; res = 0
    for l, r in order:
        if cnt[(l, r)] > 1 or mx >= r: res += cnt[(l, r)]
        mx = max(mx, r)
    return str(res)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
