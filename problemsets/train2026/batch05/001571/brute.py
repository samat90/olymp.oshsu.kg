import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    lines = s.split('\n'); m = int(lines[0]); r = []
    for i in range(m): r += list(map(int, lines[1 + i].split()[1:]))
    return ' '.join(map(str, sorted(r)))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
