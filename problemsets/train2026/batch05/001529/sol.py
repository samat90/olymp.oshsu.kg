import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    s = s.split()[0]
    m = {')': '(', ']': '[', '}': '{'}
    st = []
    for c in s:
        if c in '([{': st.append(c)
        else:
            if not st or st[-1] != m[c]: return 'NO'
            st.pop()
    return 'YES' if not st else 'NO'

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
