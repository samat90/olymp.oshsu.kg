import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    L = s.split('\n'); q = int(L[0]); t = ''; snaps = []; out = []
    for i in range(1, q + 1):
        p = L[i].split()
        if p[0] == 'type': snaps.append(t); t += p[1]
        elif p[0] == 'del': snaps.append(t); t = t[:len(t) - int(p[1])]
        elif p[0] == 'undo':
            if snaps: t = snaps.pop()
        else: out.append(t)
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
