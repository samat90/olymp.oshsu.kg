import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); T, F, n = t[:3]
    st = [(t[3 + 2 * i], t[4 + 2 * i]) for i in range(n)]
    best = -1
    for mask in range(1 << n):
        fuel = F; pos = 0; ok = True
        for i in range(n):
            if mask >> i & 1:
                x, f = st[i]
                if x - pos > fuel: ok = False; break
                fuel -= x - pos; pos = x; fuel += f
        if ok and T - pos <= fuel:
            c = bin(mask).count('1')
            if best == -1 or c < best: best = c
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
