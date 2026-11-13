import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    s = s.split()[0]
    st = []; cur = 0; num = 0
    for c in s:
        if c.isdigit(): num = num * 10 + int(c)
        elif c == '[':
            st.append((cur, num)); cur = 0; num = 0
        elif c == ']':
            prev, r = st.pop(); cur = (prev + r * cur) % MOD
        else: cur += 1
    return str(cur % MOD)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
