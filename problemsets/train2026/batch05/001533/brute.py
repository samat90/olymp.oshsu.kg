import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split()[1:]
    st = []
    for x in t:
        if x == '+' or x == '-' or x == '*':
            b = st.pop(); a = st.pop()
            st.append(eval(str(a) + x + '(' + str(b) + ')'))
        else: st.append(int(x))
    return str(st[0] % MOD)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
