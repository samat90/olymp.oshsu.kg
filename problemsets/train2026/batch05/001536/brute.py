import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    s = s.split()[0] + '/'
    while True:
        t = s.replace('//', '/').replace('/./', '/')
        t = re.sub(r'/[a-z]+/\.\./', '/', t)
        t = '/' + t[4:] if t.startswith('/../') else t
        if t == s: break
        s = t
    s = s.rstrip('/')
    return s if s else '/'

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
