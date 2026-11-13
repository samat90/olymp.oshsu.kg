import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n = int(t[0]); d = deque(t[1:1 + n]); res = []
    while d:
        res.append(d.popleft())
        if d: d.append(d.popleft())
    return ' '.join(res)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
