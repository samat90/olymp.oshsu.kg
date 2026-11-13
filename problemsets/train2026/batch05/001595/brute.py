import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n = t[0]; v = t[1:1 + n]
    res = [v[i] for i in range(n) if (i + 1) % 2 == 1] + [v[i] for i in range(n) if (i + 1) % 2 == 0]
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
