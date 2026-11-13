import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, K = t[:2]; v = t[2:2 + n]
    fast = 0
    for _ in range(K): fast += 1
    slow = -1
    while fast < n: fast += 1; slow += 1
    res = v[:slow + 1] + v[slow + 2:]
    return ' '.join(map(str, res)) or 'ПУСТО'

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
