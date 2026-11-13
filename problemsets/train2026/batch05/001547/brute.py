import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    from itertools import combinations
    t = s.split(); num = t[0]; k = int(t[1]); n = len(num)
    best = None
    for keep in combinations(range(n), n - k):
        v = int(''.join(num[i] for i in keep) or '0')
        if best is None or v < best: best = v
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
