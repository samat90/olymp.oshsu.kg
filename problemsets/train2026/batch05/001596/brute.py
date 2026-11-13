import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, K = t[:2]; v = t[2:2 + n]
    d = deque(v)
    for _ in range(K % n if K > 5000 else K): d.appendleft(d.pop())
    return ' '.join(map(str, d))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
