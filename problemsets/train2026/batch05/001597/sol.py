import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n = t[0]; v = t[1:1 + n]
    for i in range(0, n - 1, 2): v[i], v[i + 1] = v[i + 1], v[i]
    return ' '.join(map(str, v))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
