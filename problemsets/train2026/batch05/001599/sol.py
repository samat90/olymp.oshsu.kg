import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n = t[0]; v = t[1:1 + n]
    res = []; i = 0
    while i < n:
        j = i
        while j < n and v[j] == v[i]: j += 1
        if j - i == 1: res.append(v[i])
        i = j
    return ' '.join(map(str, res)) or 'ПУСТО'

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
