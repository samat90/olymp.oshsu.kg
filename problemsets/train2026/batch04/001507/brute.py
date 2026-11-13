import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import combinations
    d = d.split(); n, k = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    def rec(rest):
        if not rest: return True
        first = rest[0]; others = rest[1:]
        for c in combinations(range(len(others)), k-1):
            grp = sorted([first]+[others[i] for i in c])
            if all(grp[i+1] == grp[i]+1 for i in range(k-1)):
                if rec([others[i] for i in range(len(others)) if i not in c]): return True
        return False
    return 'YES' if n % k == 0 and rec(a) else 'NO'

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
