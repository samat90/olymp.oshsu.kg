import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    L = s.split('\n'); q = int(L[0]); st = []; h = []; dead = set(); out = []; uid = 0
    def clean():
        while st and st[-1][1] in dead: st.pop()
    for i in range(1, q + 1):
        p = L[i].split()
        if p[0] == 'push':
            x = int(p[1]); uid += 1; st.append((x, uid)); heapq.heappush(h, (-x, -uid))
        elif p[0] == 'pop':
            clean(); x, u = st.pop(); dead.add(u); out.append(str(x))
        elif p[0] == 'top':
            clean(); out.append(str(st[-1][0]))
        else:
            while -h[0][1] in dead: heapq.heappop(h)
            x, u = h[0]
            if p[0] == 'peekMax': out.append(str(-x))
            else: heapq.heappop(h); dead.add(-u); out.append(str(-x))
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
