import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    s = d.strip(); n = len(s); cuts = [0]
    for i in range(1, n):
        if not (set(s[:i]) & set(s[i:])): cuts.append(i)
    cuts.append(n)
    return str(len(cuts)-1) + '\n' + ' '.join(str(cuts[i+1]-cuts[i]) for i in range(len(cuts)-1))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
