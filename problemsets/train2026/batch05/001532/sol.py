import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    s = s.split()[0]
    st = [-1]; best = 0
    for i, c in enumerate(s):
        if c == '(': st.append(i)
        else:
            st.pop()
            if not st: st.append(i)
            else: best = max(best, i - st[-1])
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
