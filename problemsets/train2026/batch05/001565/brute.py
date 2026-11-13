import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, w = t[0], t[1]; a = t[2:2 + n]
    return ' '.join(str(sum(1 for j in range(i + 1) if a[j] >= a[i] - w)) for i in range(n))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
