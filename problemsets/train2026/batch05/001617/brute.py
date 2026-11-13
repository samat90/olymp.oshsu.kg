import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    L = s.split('\n'); n, m = map(int, L[0].split()); ev = []
    for i in range(1, m + 1):
        f, kind, t = L[i].split(); ev.append((int(f), kind, int(t)))
    T = max(e[2] for e in ev); res = [0] * n; st = []; j = 0
    for t in range(T + 1):
        while j < m and ev[j][2] == t and ev[j][1] == 'start':
            st.append(ev[j][0]); j += 1
        if st: res[st[-1]] += 1
        while j < m and ev[j][2] == t and ev[j][1] == 'end':
            st.pop(); j += 1
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
