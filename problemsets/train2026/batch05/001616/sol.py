import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    L = s.split('\n'); q = int(L[0]); h = []; out = []
    for i in range(1, q + 1):
        p = L[i].split()
        if p[0] == 'come': heapq.heappush(h, (-int(p[2]), i, p[1]))
        else: out.append(heapq.heappop(h)[2] if h else '-')
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
