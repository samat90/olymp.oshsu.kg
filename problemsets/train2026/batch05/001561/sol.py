import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, m = t[0], t[1]
    h = [(0, i) for i in range(m)]; res = []
    for i in range(n):
        a, d = t[2 + 2 * i], t[3 + 2 * i]
        f, c = heapq.heappop(h)
        e = max(a, f) + d
        res.append(e); heapq.heappush(h, (e, c))
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
