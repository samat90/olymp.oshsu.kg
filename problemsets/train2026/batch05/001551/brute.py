import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split(); n, w = int(t[0]), int(t[1]); a = list(map(int, t[2:2 + n]))
    return ' '.join(str(max(a[i:i + w])) for i in range(n - w + 1))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
