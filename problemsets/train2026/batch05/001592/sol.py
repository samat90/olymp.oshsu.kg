import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n = t[0]; nx = [0] + t[1:1 + n]
    a = b = 1
    while True:
        if b == 0 or nx[b] == 0: return '-1'
        a = nx[a]; b = nx[nx[b]]
        if a == b: break
        if b == 0: return '-1'
    a = 1
    while a != b: a = nx[a]; b = nx[b]
    return str(a)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
