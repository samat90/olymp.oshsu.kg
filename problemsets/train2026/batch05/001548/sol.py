import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n, K = int(t[0]), int(t[1]); a = list(map(int, t[2:2 + n]))
    st = []
    for i, x in enumerate(a):
        while st and st[-1] > x and len(st) + n - i > K: st.pop()
        if len(st) < K: st.append(x)
    return ' '.join(map(str, st))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
