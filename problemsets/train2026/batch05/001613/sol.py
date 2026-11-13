import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    L = s.split('\n'); h = [L[0]]; pos = 0; end = 1; q = int(L[1]); out = []
    for i in range(2, 2 + q):
        p = L[i].split()
        if p[0] == 'visit':
            pos += 1
            if pos < len(h): h[pos] = p[1]
            else: h.append(p[1])
            end = pos + 1
        else:
            kk = int(p[1])
            pos = max(0, pos - kk) if p[0] == 'back' else min(end - 1, pos + kk)
            out.append(h[pos])
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
