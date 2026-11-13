import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); ev = []
    for i in range(n): ev.append((int(d[1+2*i]), 0)); ev.append((int(d[2+2*i]), 1))
    ev.sort(); cur = best = 0
    for _, t in ev:
        if t == 0: cur += 1; best = max(best, cur)
        else: cur -= 1
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
