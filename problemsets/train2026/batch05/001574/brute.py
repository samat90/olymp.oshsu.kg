import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split(); n = int(t[0]); a = tuple(sorted(int(x) for x in t[1:1 + n]))
    memo = {}
    def f(st):
        if len(st) == 1: return 0
        if st in memo: return memo[st]
        best = None
        for i in range(len(st)):
            for j in range(i + 1, len(st)):
                r = list(st); x = r[i] + r[j]; del r[j]; del r[i]; r.append(x)
                v = x + f(tuple(sorted(r)))
                if best is None or v < best: best = v
        memo[st] = best
        return best
    return str(f(a))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
