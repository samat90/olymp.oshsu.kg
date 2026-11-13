import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n = int(t[0]); a = list(map(int, t[1:1 + n]))
    st = []
    for i in range(n):
        if not st or a[st[-1]] > a[i]: st.append(i)
    best = 0
    for j in range(n - 1, -1, -1):
        while st and a[st[-1]] <= a[j]:
            best = max(best, j - st.pop())
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
