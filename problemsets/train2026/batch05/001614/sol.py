import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    L = s.split('\n'); q = int(L[0]); txt = []; hist = []; out = []
    for i in range(1, q + 1):
        p = L[i].split()
        if p[0] == 'type':
            txt.extend(p[1]); hist.append(('t', len(p[1])))
        elif p[0] == 'del':
            kk = int(p[1]); rem = txt[len(txt) - kk:] if kk else []
            del txt[len(txt) - kk:]; hist.append(('d', rem))
        elif p[0] == 'undo':
            if hist:
                a, b = hist.pop()
                if a == 't': del txt[len(txt) - b:]
                else: txt.extend(b)
        else: out.append(''.join(txt))
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
