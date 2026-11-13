import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); a = t[1:1 + t[0]]
    while True:
        for i in range(len(a) - 1):
            if a[i] > 0 and a[i + 1] < 0:
                x, y = a[i], -a[i + 1]
                if x > y: del a[i + 1]
                elif x < y: del a[i]
                else: del a[i:i + 2]
                break
        else: break
    return ' '.join(map(str, a)) or 'ПУСТО'

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
