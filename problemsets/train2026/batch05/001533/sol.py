import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split()[1:]
    st = []
    for x in t:
        if x in '+-*' and len(x) == 1 and not x.isdigit():
            b = st.pop(); a = st.pop()
            st.append((a + b) % MOD if x == '+' else (a - b) % MOD if x == '-' else a * b % MOD)
        else: st.append(int(x))
    return str(st[0] % MOD)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
