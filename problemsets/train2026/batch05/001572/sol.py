import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n, K = int(t[0]), int(t[1]); a = t[2:2 + n]
    c = Counter(map(int, a))
    return ' '.join(str(v) for _, v in heapq.nsmallest(K, ((-f, v) for v, f in c.items())))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
