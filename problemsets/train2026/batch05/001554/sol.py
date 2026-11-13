import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    s = s.split()[0]
    last = {c: i for i, c in enumerate(s)}
    st = []; seen = set()
    for i, c in enumerate(s):
        if c in seen: continue
        while st and st[-1] > c and last[st[-1]] > i:
            seen.discard(st.pop())
        st.append(c); seen.add(c)
    return ''.join(st)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
