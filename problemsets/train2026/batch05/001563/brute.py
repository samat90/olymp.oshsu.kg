import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, p = t[0], t[1]; a = t[2:2 + n]
    d = deque(range(n)); sec = 0
    while True:
        i = d.popleft(); sec += 1; a[i] -= 1
        if a[i] == 0:
            if i == p - 1: return str(sec)
        else: d.append(i)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
