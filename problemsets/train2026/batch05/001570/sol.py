import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n = int(t[0]); a = list(map(int, t[1:1 + n]))
    lo = []; up = []; res = []
    for x in a:
        heapq.heappush(lo, -x)
        heapq.heappush(up, -heapq.heappop(lo))
        if len(up) > len(lo): heapq.heappush(lo, -heapq.heappop(up))
        res.append(-lo[0])
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
