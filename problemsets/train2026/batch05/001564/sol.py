import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = s.split(); n = int(t[0]); a = t[1:1 + n]; b = t[1 + n:1 + 2 * n]
    c = [a.count('0'), a.count('1')]
    for x in b:
        if c[int(x)] == 0: break
        c[int(x)] -= 1
    return str(sum(c))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
