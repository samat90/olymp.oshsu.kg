import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    L = s.split('\n'); q = int(L[0]); a = []; out = []
    for i in range(1, q + 1):
        p = L[i].split()
        if p[0] == 'come': a.append((int(p[2]), i, p[1]))
        elif not a: out.append('-')
        else:
            best = a[0]
            for x in a:
                if x[0] > best[0] or (x[0] == best[0] and x[1] < best[1]): best = x
            a.remove(best); out.append(best[2])
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
