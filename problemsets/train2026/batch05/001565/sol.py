import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, w = t[0], t[1]; a = t[2:2 + n]
    d = deque(); res = []
    for x in a:
        d.append(x)
        while d[0] < x - w: d.popleft()
        res.append(len(d))
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
