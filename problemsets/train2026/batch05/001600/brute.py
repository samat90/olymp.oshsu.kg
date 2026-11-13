import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n, m = t[:2]; a = t[2:2 + n]; b = t[2 + n:2 + n + m]
    sys.set_int_max_str_digits(0)
    f = lambda d: int(''.join(map(str, d[::-1])))
    return ' '.join(str(f(a) + f(b))[::-1])

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
