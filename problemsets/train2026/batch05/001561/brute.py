import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, m = t[0], t[1]
    free = [0] * m; res = []
    for i in range(n):
        a, d = t[2 + 2 * i], t[3 + 2 * i]
        c = min(range(m), key=lambda j: (free[j], j))
        free[c] = max(a, free[c]) + d
        res.append(free[c])
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
