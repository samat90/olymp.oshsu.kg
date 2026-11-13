import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    s = s.split()[0]; n = len(s); st = [Counter()]; i = 0
    while i < n:
        c = s[i]
        if c == '(': st.append(Counter()); i += 1
        elif c == ')':
            i += 1; j = i
            while j < n and s[j].isdigit(): j += 1
            m = int(s[i:j] or 1); i = j; top = st.pop()
            for e, v in top.items(): st[-1][e] += v * m
        else:
            j = i + 1
            while j < n and s[j].islower(): j += 1
            e = s[i:j]; i = j
            while j < n and s[j].isdigit(): j += 1
            st[-1][e] += int(s[i:j] or 1); i = j
    return ''.join(e + (str(v) if v > 1 else '') for e, v in sorted(st[0].items()))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
