import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n, K = int(t[0]), int(t[1]); a = list(map(int, t[2:2 + n]))
    h = []; res = []
    for x in a:
        if len(h) < K: heapq.heappush(h, x)
        elif x > h[0]: heapq.heapreplace(h, x)
        res.append(h[0] if len(h) == K else -1)
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
