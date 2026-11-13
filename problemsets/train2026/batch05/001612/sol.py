import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    from collections import OrderedDict
    L = s.split('\n'); cap, q = map(int, L[0].split()); d = OrderedDict(); out = []
    for i in range(1, q + 1):
        p = L[i].split()
        if p[0] == 'put':
            d[p[1]] = p[2]; d.move_to_end(p[1])
            if len(d) > cap: d.popitem(last=False)
        else:
            if p[1] in d: d.move_to_end(p[1]); out.append(d[p[1]])
            else: out.append('-1')
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
