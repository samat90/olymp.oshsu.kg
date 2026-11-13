import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n = t[0]
    a = [t[1 + 2 * i] for i in range(n)]; d = [t[2 + 2 * i] for i in range(n)]
    done = [False] * n; now = 0; res = []
    for _ in range(n):
        av = [i for i in range(n) if not done[i] and a[i] <= now]
        if not av:
            now = min(a[i] for i in range(n) if not done[i])
            av = [i for i in range(n) if not done[i] and a[i] <= now]
        j = min(av, key=lambda i: (d[i], i)); done[j] = True; now += d[j]; res.append(j + 1)
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
