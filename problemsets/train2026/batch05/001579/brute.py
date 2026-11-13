import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n = t[0]
    iv = [(t[1 + 2 * i], t[2 + 2 * i]) for i in range(n)]
    return str(max(sum(1 for a, b in iv if a <= x < b) for x, _ in iv))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
