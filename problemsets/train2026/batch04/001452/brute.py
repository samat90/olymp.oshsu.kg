import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n]))
    o = []; e = []
    for x in a:
        t = o if x % 2 else e
        t.append(x)
        i = len(t)-1
        while i > 0 and ((t[i-1] > t[i]) if x % 2 else (t[i-1] < t[i])):
            t[i-1], t[i] = t[i], t[i-1]; i -= 1
    return ' '.join(map(str, o + e))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
