import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, l, r = t[:3]; v = t[3:3 + n]
    nxt = list(range(1, n + 1)) + [0]; nxt[n] = -1
    head = 0
    prev = -1; cur = head
    for _ in range(l - 1): prev = cur; cur = nxt[cur]
    tail = cur; p = -1
    for _ in range(r - l + 1):
        q = nxt[cur]; nxt[cur] = p; p = cur; cur = q
    if prev == -1: head = p
    else: nxt[prev] = p
    nxt[tail] = cur
    res = []; c = head
    while c != -1 and c < n: res.append(v[c]); c = nxt[c]
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
