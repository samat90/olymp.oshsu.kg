import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n = t[0]; st = []
    for x in t[1:1 + n]:
        alive = True
        while alive and x < 0 and st and st[-1] > 0:
            if st[-1] < -x: st.pop()
            elif st[-1] == -x: st.pop(); alive = False
            else: alive = False
        if alive: st.append(x)
    return ' '.join(map(str, st)) or 'ПУСТО'

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
