import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    s = s.split()[0]
    def dec(i):
        res = ''; num = 0
        while i < len(s) and s[i] != ']':
            c = s[i]
            if c.isdigit(): num = num * 10 + int(c); i += 1
            elif c == '[':
                inner, i = dec(i + 1)
                res += inner * num; num = 0; i += 1
            else: res += c; i += 1
        return res, i
    return str(len(dec(0)[0]) % MOD)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
