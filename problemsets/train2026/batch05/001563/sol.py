import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, p = t[0], t[1]; a = t[2:2 + n]; x = a[p - 1]
    return str(sum(min(a[i], x if i < p else x - 1) for i in range(n)))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
