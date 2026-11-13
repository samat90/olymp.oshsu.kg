import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n, w = int(t[0]), int(t[1]); a = list(map(int, t[2:2 + n]))
    dq = deque(); res = []
    for i in range(n):
        while dq and a[dq[-1]] <= a[i]: dq.pop()
        dq.append(i)
        if dq[0] <= i - w: dq.popleft()
        if i >= w - 1: res.append(a[dq[0]])
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
