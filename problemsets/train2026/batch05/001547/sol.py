import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); num = t[0]; k = int(t[1])
    st = []
    for c in num:
        while k and st and st[-1] > c: st.pop(); k -= 1
        st.append(c)
    if k: st = st[:-k]
    return (''.join(st).lstrip('0')) or '0'

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
