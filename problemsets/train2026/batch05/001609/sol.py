import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    L = s.split('\n'); q = int(L[0]); st = []; out = []
    for i in range(1, q + 1):
        p = L[i].split()
        if p[0] == 'push':
            x = int(p[1]); st.append((x, min(x, st[-1][1]) if st else x))
        elif p[0] == 'pop': st.pop()
        elif p[0] == 'top': out.append(str(st[-1][0]))
        else: out.append(str(st[-1][1]))
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
