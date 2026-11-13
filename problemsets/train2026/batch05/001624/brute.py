import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n = t[0]; a = t[1:1 + n]; b = sorted(a)
    return str(1 + sum(1 for i in range(1, n) if sorted(a[:i]) == b[:i]))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
