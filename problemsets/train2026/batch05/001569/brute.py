import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = s.split(); n, K = int(t[0]), int(t[1]); a = list(map(int, t[2:2 + n]))
    return ' '.join(str(sorted(a[:i + 1], reverse=True)[K - 1]) if i + 1 >= K else '-1' for i in range(n))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
