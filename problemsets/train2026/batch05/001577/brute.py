import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    from itertools import permutations
    s = s.split()[0]
    for p in sorted(set(permutations(s))):
        if all(p[i] != p[i + 1] for i in range(len(p) - 1)): return ''.join(p)
    return 'НЕТ'

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
