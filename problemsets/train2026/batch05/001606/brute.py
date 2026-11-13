import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    lines = s.split('\n'); n = int(lines[0]); v = list(map(int, lines[1].split())); q = int(lines[2])
    for i in range(q):
        p = lines[3 + i].split()
        if p[0] == 'remove': v.remove(int(p[1]))
        elif p[0] == 'after': v.insert(v.index(int(p[1])) + 1, int(p[2]))
        else: v.insert(v.index(int(p[1])), int(p[2]))
    return ' '.join(map(str, v)) or 'ПУСТО'

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
