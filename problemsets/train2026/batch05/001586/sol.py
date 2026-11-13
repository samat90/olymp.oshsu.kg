import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, K = t[0], t[1]; c = sorted(t[2:2 + n], reverse=True) + [0]
    rev = 0
    for i in range(n):
        w = i + 1; cur = c[i]; nxt = c[i + 1]; cnt = w * (cur - nxt)
        if K >= cnt:
            rev += w * (cur + nxt + 1) * (cur - nxt) // 2; K -= cnt
        else:
            full, rem = divmod(K, w)
            rev += w * (2 * cur - full + 1) * full // 2 + rem * (cur - full); K = 0
        if K == 0: break
    return str(rev % MOD)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
