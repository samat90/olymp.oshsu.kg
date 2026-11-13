import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    s = d.strip(); last = {ch: i for i, ch in enumerate(s)}; res = []; st_ = 0; end = 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])
        if i == end: res.append(i-st_+1); st_ = i+1
    return str(len(res)) + '\n' + ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
