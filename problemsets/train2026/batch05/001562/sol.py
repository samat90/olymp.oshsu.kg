import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, q = t[0], t[1]; b = t[2:2 + n]
    d = deque(range(n)); res = [0] * n; now = 0
    while d:
        i = d.popleft(); x = min(q, b[i]); now += x; b[i] -= x
        if b[i]: d.append(i)
        else: res[i] = now
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
