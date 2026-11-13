import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    s = s.split()[0]
    st = []
    for p in s.split('/'):
        if p == '' or p == '.': continue
        if p == '..':
            if st: st.pop()
        else: st.append(p)
    return '/' + '/'.join(st)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
