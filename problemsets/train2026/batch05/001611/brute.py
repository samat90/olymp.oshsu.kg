import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    L = s.split('\n'); cap, q = map(int, L[0].split()); st = []; out = []
    for i in range(1, q + 1):
        p = L[i].split()
        if p[0] == 'push':
            if len(st) < cap: st.append(int(p[1]))
        elif p[0] == 'pop': out.append(str(st.pop() if st else -1))
        else:
            for j in range(min(int(p[1]), len(st))): st[j] += int(p[2])
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
