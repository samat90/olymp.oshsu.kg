import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split(); n = int(t[0]); a = list(map(int, t[1:1 + n]))
    res = []
    for i in range(n):
        c = 0
        for j in range(i + 1, n):
            if all(a[m] < min(a[i], a[j]) for m in range(i + 1, j)): c += 1
        res.append(c)
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
