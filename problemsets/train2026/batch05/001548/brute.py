import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    from itertools import combinations
    t = s.split(); n, K = int(t[0]), int(t[1]); a = list(map(int, t[2:2 + n]))
    return ' '.join(map(str, min([a[i] for i in c] for c in combinations(range(n), K))))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
