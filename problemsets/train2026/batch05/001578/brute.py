import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, m, K = t[:3]; a = t[3:3 + n]; b = t[3 + n:3 + n + m]
    return ' '.join(map(str, sorted(x + y for x in a for y in b)[:K]))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
