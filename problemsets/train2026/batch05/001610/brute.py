import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    L = s.split('\n'); q = int(L[0]); a = []; out = []
    for i in range(1, q + 1):
        p = L[i].split()
        if p[0] == 'push': a.append(int(p[1]))
        elif p[0] == 'pop': out.append(str(a.pop()))
        elif p[0] == 'top': out.append(str(a[-1]))
        elif p[0] == 'peekMax': out.append(str(max(a)))
        else:
            m = max(a); j = len(a) - 1
            while a[j] != m: j -= 1
            del a[j]; out.append(str(m))
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
