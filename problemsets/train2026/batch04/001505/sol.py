import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    s, k = d.split(); k = int(k); st_ = []
    for ch in s:
        while k and st_ and st_[-1] > ch: st_.pop(); k -= 1
        st_.append(ch)
    if k: st_ = st_[:-k]
    return ''.join(st_).lstrip('0') or '0'

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
