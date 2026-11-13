import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split(); n = int(t[0]); a = list(map(int, t[1:1 + n]))
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if a[i] < a[k] < a[j]: return 'YES'
    return 'NO'

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
