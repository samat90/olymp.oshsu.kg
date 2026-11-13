import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n, m = int(t[0]), int(t[1]); g = t[2:2 + n]
    h = [0] * (m + 1); best = 0
    for row in g:
        for j in range(m): h[j] = h[j] + 1 if row[j] == '1' else 0
        st = []
        for i in range(m + 1):
            while st and h[st[-1]] >= h[i]:
                x = h[st.pop()]
                l = st[-1] if st else -1
                best = max(best, x * (i - l - 1))
            st.append(i)
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
