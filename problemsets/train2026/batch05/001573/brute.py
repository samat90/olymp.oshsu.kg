import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split(); n = int(t[0]); a = sorted(int(x) for x in t[1:1 + n])
    while len(a) > 1:
        y = a.pop(); x = a.pop()
        if y != x: a.append(y - x); a.sort()
    return str(a[0]) if a else '0'

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
