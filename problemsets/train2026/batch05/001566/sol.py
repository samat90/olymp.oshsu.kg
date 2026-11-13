import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, w, m = t[0], t[1], t[2]; a = t[3:3 + n]
    d = deque(); res = []
    for x in a:
        while d and d[0] <= x - w: d.popleft()
        if len(d) < m: d.append(x); res.append('YES')
        else: res.append('NO')
    return ' '.join(res)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
