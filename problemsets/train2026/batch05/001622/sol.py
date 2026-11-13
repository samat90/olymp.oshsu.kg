import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    s = s.split()[0]; n = len(s); pair = [0] * n; st = []
    for i, c in enumerate(s):
        if c == '(': st.append(i)
        elif c == ')': j = st.pop(); pair[i] = j; pair[j] = i
    res = []; i = 0; d = 1
    while 0 <= i < n:
        if s[i] in '()': i = pair[i]; d = -d
        else: res.append(s[i])
        i += d
    return ''.join(res)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
