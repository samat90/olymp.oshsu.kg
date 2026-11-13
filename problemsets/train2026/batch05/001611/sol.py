import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    L = s.split('\n'); cap, q = map(int, L[0].split())
    st = []; add = []; out = []
    for i in range(1, q + 1):
        p = L[i].split()
        if p[0] == 'push':
            if len(st) < cap: st.append(int(p[1])); add.append(0)
        elif p[0] == 'pop':
            if not st: out.append('-1')
            else:
                a = add.pop(); x = st.pop()
                if add: add[-1] += a
                out.append(str(x + a))
        else:
            kk = min(int(p[1]), len(st))
            if kk: add[kk - 1] += int(p[2])
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
