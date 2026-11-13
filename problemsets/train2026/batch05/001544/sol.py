import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n = int(t[0]); a = list(map(int, t[1:1 + n]))
    left = [0] * n; right = [0] * n; st = []
    for i in range(n):
        while st and a[st[-1]] >= a[i]: st.pop()
        left[i] = i - (st[-1] if st else -1); st.append(i)
    st = []
    for i in range(n - 1, -1, -1):
        while st and a[st[-1]] > a[i]: st.pop()
        right[i] = (st[-1] if st else n) - i; st.append(i)
    return str(sum(a[i] * left[i] * right[i] for i in range(n)) % MOD)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
