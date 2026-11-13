import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    t = list(map(int, s.split())); n = t[0]; target = tuple(t[1:1 + n])
    seen = set()
    def go(nxt, st, out):
        if (nxt, st, out) in seen: return False
        seen.add((nxt, st, out))
        if len(out) == n: return out == target
        if out != target[:len(out)]: return False
        if nxt <= n and go(nxt + 1, st + (nxt,), out): return True
        if st and go(nxt, st[:-1], out + (st[-1],)): return True
        return False
    return 'YES' if go(1, (), ()) else 'NO'

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
