import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    s = s.split()[0]; n = len(s); need = len(set(s)); best = None
    for mask in range(1, 1 << n):
        t = ''.join(s[i] for i in range(n) if mask >> i & 1)
        if len(t) == need and len(set(t)) == need:
            if best is None or t < best: best = t
    return best

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
