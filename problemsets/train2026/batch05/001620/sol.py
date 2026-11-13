import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n = int(t[0]); st = []
    for x in t[1:1 + n]:
        if x == '+': st.append((st[-1] + st[-2]) % MOD)
        elif x == 'D': st.append(st[-1] * 2 % MOD)
        elif x == 'C': st.pop()
        else: st.append(int(x) % MOD)
    return str(sum(st) % MOD)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
