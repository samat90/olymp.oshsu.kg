import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n = int(t[0]); a = list(map(int, t[1:1 + n]))
    res = [0] * n; st = []
    for i in range(n):
        while st and a[st[-1]] < a[i]:
            j = st.pop(); res[j] = i - j
        st.append(i)
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
