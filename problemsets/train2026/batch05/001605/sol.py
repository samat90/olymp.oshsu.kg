import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n = t[0]; v = t[1:1 + n]
    c = 0
    for i in range(n - 1, -1, -1):
        x = v[i] * 2 + c; v[i] = x % 10; c = x // 10
    if c: v = [c] + v
    return ' '.join(map(str, v))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
