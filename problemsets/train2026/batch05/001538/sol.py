import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); K = int(t[0]); s = t[1]
    st = []
    for c in s:
        if st and st[-1][0] == c:
            st[-1][1] += 1
            if st[-1][1] == K: st.pop()
        else: st.append([c, 1])
    return ''.join(c * n for c, n in st) or 'ПУСТО'

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
