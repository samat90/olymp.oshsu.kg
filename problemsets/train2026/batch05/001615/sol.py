import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    L = s.split('\n'); q = int(L[0]); freq = {}; groups = {}; mx = 0; out = []
    for i in range(1, q + 1):
        p = L[i].split()
        if p[0] == 'push':
            x = p[1]; f = freq.get(x, 0) + 1; freq[x] = f
            groups.setdefault(f, []).append(x); mx = max(mx, f)
        else:
            x = groups[mx].pop(); freq[x] -= 1; out.append(x)
            if not groups[mx]: mx -= 1
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
