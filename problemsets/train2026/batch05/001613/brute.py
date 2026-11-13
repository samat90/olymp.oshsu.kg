import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    L = s.split('\n'); back = []; cur = L[0]; fwd = []; q = int(L[1]); out = []
    for i in range(2, 2 + q):
        p = L[i].split()
        if p[0] == 'visit': back.append(cur); cur = p[1]; fwd = []
        elif p[0] == 'back':
            for _ in range(min(int(p[1]), len(back))): fwd.append(cur); cur = back.pop()
            out.append(cur)
        else:
            for _ in range(min(int(p[1]), len(fwd))): back.append(cur); cur = fwd.pop()
            out.append(cur)
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
