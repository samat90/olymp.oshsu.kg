import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n = int(t[0]); a = list(map(int, t[1:1 + n]))
    res = [0] * n; st = []
    for i in range(n - 1, -1, -1):
        c = 0
        while st and st[-1] < a[i]:
            st.pop(); c += 1
        if st: c += 1
        res[i] = c; st.append(a[i])
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
