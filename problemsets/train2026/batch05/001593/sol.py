import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, m = t[:2]; a = t[2:2 + n]; b = t[2 + n:2 + n + m]
    i = j = 0; res = []
    while i < n and j < m:
        if a[i] <= b[j]: res.append(a[i]); i += 1
        else: res.append(b[j]); j += 1
    res += a[i:] + b[j:]
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
