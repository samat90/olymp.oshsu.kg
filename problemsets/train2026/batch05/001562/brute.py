import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, q = t[0], t[1]; b = t[2:2 + n]
    res = [0] * n; now = 0; left = n
    while left:
        for i in range(n):
            if b[i] > 0:
                x = min(q, b[i]); now += x; b[i] -= x
                if b[i] == 0: res[i] = now; left -= 1
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
