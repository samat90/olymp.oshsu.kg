import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n, L = int(t[0]), int(t[1]); a = list(map(int, t[2:2 + n]))
    mx = deque(); mn = deque(); l = 0; best = 0
    for i in range(n):
        while mx and a[mx[-1]] <= a[i]: mx.pop()
        mx.append(i)
        while mn and a[mn[-1]] >= a[i]: mn.pop()
        mn.append(i)
        while a[mx[0]] - a[mn[0]] > L:
            l += 1
            if mx[0] < l: mx.popleft()
            if mn[0] < l: mn.popleft()
        best = max(best, i - l + 1)
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
