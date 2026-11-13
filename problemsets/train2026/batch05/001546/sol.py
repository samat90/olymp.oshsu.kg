import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n = int(t[0]); a = list(map(int, t[1:1 + n]))
    st = []; tot = 0
    for i in range(n):
        while st and a[st[-1]] < a[i]:
            m = a[st.pop()]
            if not st: break
            tot += (min(a[st[-1]], a[i]) - m) * (i - st[-1] - 1)
        st.append(i)
    return str(tot)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
