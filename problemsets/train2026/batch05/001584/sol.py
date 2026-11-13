import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, K = t[0], t[1]
    it = ((t[2 + 2 * i] ** 2 + t[3 + 2 * i] ** 2, i + 1) for i in range(n))
    return ' '.join(str(i) for _, i in heapq.nsmallest(K, it))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
