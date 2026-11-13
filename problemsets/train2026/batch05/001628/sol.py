import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n = t[0]; v = sorted(t[1:1 + n])
    d = deque(range(n)); res = [0] * n
    for x in v:
        res[d.popleft()] = x
        if d: d.append(d.popleft())
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
