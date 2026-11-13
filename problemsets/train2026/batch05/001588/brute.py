import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split(); cnt = Counter(t[0]); c = int(t[1]); L = sorted(cnt)
    start = (tuple(cnt[x] for x in L), tuple(0 for _ in L))
    cur = {start}; time = 0
    while True:
        for st in cur:
            if sum(st[0]) == 0: return str(time)
        nxt = set()
        for rem, cd in cur:
            ncd = tuple(max(0, x - 1) for x in cd)
            nxt.add((rem, ncd))
            for i in range(len(L)):
                if rem[i] and cd[i] == 0:
                    r2 = list(rem); r2[i] -= 1; c2 = list(ncd); c2[i] = c
                    nxt.add((tuple(r2), tuple(c2)))
        cur = nxt; time += 1

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
