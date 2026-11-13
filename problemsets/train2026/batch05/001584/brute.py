import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, K = t[0], t[1]
    L = sorted(range(n), key=lambda i: (t[2 + 2 * i] ** 2 + t[3 + 2 * i] ** 2, i))
    return ' '.join(str(i + 1) for i in L[:K])

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
