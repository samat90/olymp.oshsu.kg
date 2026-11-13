import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split(); n = int(t[0]); a = [None]
    for x in t[1:1 + n]:
        a.append(int(x)); i = len(a) - 1
        while i > 1 and a[i] < a[i // 2]:
            a[i], a[i // 2] = a[i // 2], a[i]; i //= 2
    return ' '.join(map(str, a[1:]))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
