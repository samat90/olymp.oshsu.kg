import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    L = s.split('\n'); cap, q = map(int, L[0].split()); keys = []; val = {}; out = []
    for i in range(1, q + 1):
        p = L[i].split()
        if p[0] == 'put':
            if p[1] in keys: keys.remove(p[1])
            keys.append(p[1]); val[p[1]] = p[2]
            if len(keys) > cap: del val[keys.pop(0)]
        else:
            if p[1] in keys: keys.remove(p[1]); keys.append(p[1]); out.append(val[p[1]])
            else: out.append('-1')
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
