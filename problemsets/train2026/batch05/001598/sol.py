import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, K = t[:2]; v = t[2:2 + n]
    for i in range(0, n - K + 1, K): v[i:i + K] = v[i:i + K][::-1]
    return ' '.join(map(str, v))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
