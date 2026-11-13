import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); cnt = Counter(t[0]); c = int(t[1])
    m = max(cnt.values()); k = sum(1 for v in cnt.values() if v == m)
    return str(max(len(t[0]), (m - 1) * (c + 1) + k))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
