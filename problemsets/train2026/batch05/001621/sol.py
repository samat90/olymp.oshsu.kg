import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    s = s.split()[0]; st = [0]
    for c in s:
        if c == '(': st.append(0)
        else:
            v = st.pop(); st[-1] = (st[-1] + max(2 * v, 1)) % MOD
    return str(st[0] % MOD)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
