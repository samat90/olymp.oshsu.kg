import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, K = t[:2]; a = t[2:2 + n]
    p = [0]
    for x in a: p.append(p[-1] + x)
    dq = deque(); best = n + 1
    for i in range(n + 1):
        while dq and p[i] - p[dq[0]] >= K:
            best = min(best, i - dq.popleft())
        while dq and p[dq[-1]] >= p[i]: dq.pop()
        dq.append(i)
    return str(best if best <= n else -1)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
