import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    L = s.split('\n'); q = int(L[0]); a = []; out = []
    for i in range(1, q + 1):
        p = L[i].split()
        if p[0] == 'push': a.append(p[1])
        else:
            m = max(a.count(x) for x in a)
            j = max(i2 for i2 in range(len(a)) if a.count(a[i2]) == m)
            out.append(a.pop(j))
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
