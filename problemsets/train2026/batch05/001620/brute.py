import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split(); n = int(t[0]); a = []
    for x in t[1:1 + n]:
        if x == '+': a.append(a[-1] + a[-2])
        elif x == 'D': a.append(a[-1] * 2)
        elif x == 'C': a = a[:-1]
        else: a.append(int(x))
    return str(sum(a) % MOD)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
