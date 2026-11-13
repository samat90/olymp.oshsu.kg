import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, w, m = t[0], t[1], t[2]; a = t[3:3 + n]
    acc = []; res = []
    for x in a:
        if sum(1 for y in acc if x - w < y <= x) < m: acc.append(x); res.append('YES')
        else: res.append('NO')
    return ' '.join(res)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
