import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    s = s.split()[0]
    while True:
        for i in range(len(s) - 1):
            if s[i] == s[i + 1]:
                s = s[:i] + s[i + 2:]; break
        else: break
    return s or 'ПУСТО'

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
