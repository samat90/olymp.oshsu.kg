import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n = int(t[0]); a = list(map(int, t[1:1 + n])) + [0]
    st = []; best = 0
    for i, h in enumerate(a):
        while st and a[st[-1]] >= h:
            x = a[st.pop()]
            l = st[-1] if st else -1
            best = max(best, x * (i - l - 1))
        st.append(i)
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
