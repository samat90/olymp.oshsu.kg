import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    s = d.strip(); last = {c: i for i, c in enumerate(s)}; stk = []; seen = set()
    for i, c in enumerate(s):
        if c in seen: continue
        while stk and stk[-1] > c and last[stk[-1]] > i: seen.discard(stk.pop())
        stk.append(c); seen.add(c)
    return ''.join(stk)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
