import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n = t[0]; st = []; nxt = 1
    for x in t[1:1 + n]:
        while nxt <= x: st.append(nxt); nxt += 1
        if st[-1] != x: return 'NO'
        st.pop()
    return 'YES'

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
