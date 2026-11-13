import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    lines = s.split('\n'); n = int(lines[0]); v = list(map(int, lines[1].split()))
    nx = {}; pv = {}
    H = 'H'; T = 'T'
    seq = [H] + v + [T]
    for i in range(len(seq) - 1): nx[seq[i]] = seq[i + 1]; pv[seq[i + 1]] = seq[i]
    q = int(lines[2])
    for i in range(q):
        p = lines[3 + i].split()
        if p[0] == 'remove':
            x = int(p[1]); a = pv[x]; b = nx[x]; nx[a] = b; pv[b] = a
        else:
            x = int(p[1]); y = int(p[2])
            if p[0] == 'after': a, b = x, nx[x]
            else: a, b = pv[x], x
            nx[a] = y; pv[y] = a; nx[y] = b; pv[b] = y
    res = []; c = nx[H]
    while c != T: res.append(c); c = nx[c]
    return ' '.join(map(str, res)) or 'ПУСТО'

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
