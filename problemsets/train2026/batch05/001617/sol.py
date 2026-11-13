import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    L = s.split('\n'); n, m = map(int, L[0].split()); res = [0] * n; st = []; prev = 0
    for i in range(1, m + 1):
        f, kind, t = L[i].split(); f = int(f); t = int(t)
        if kind == 'start':
            if st: res[st[-1]] += t - prev
            st.append(f); prev = t
        else:
            res[st.pop()] += t - prev + 1; prev = t + 1
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
