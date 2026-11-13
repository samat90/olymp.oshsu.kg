import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, m = t[:2]; a = t[2:2 + n]; b = t[2 + n:2 + n + m]
    res = []; c = 0
    for i in range(max(n, m)):
        x = (a[i] if i < n else 0) + (b[i] if i < m else 0) + c
        res.append(x % 10); c = x // 10
    if c: res.append(c)
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
