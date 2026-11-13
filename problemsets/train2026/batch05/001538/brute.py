import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split(); K = int(t[0]); s = t[1]
    while True:
        i = 0; found = False
        while i < len(s):
            j = i
            while j < len(s) and s[j] == s[i]: j += 1
            if j - i >= K:
                s = s[:i] + s[i + K:]; found = True; break
            i = j
        if not found: break
    return s or 'ПУСТО'

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
