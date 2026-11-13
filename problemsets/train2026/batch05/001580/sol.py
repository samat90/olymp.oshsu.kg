import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); T, F, n = t[:3]
    st = [(t[3 + 2 * i], t[4 + 2 * i]) for i in range(n)] + [(T, 0)]
    h = []; fuel = F; pos = 0; cnt = 0
    for x, f in st:
        fuel -= x - pos; pos = x
        while fuel < 0 and h:
            fuel += -heapq.heappop(h); cnt += 1
        if fuel < 0: return '-1'
        heapq.heappush(h, -f)
    return str(cnt)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
