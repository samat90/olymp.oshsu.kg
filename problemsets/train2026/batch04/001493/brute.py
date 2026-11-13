import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, p = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    best = [10**18]
    def rec(used, cnt, cur, start):
        if cnt == p: best[0] = min(best[0], cur); return
        for i in range(n):
            if used >> i & 1: continue
            for j in range(i+1, n):
                if used >> j & 1: continue
                rec(used | 1 << i | 1 << j, cnt+1, max(cur, abs(a[i]-a[j])), 0)
            break  # самый левый свободный: либо в паре, либо пропущен
        # пропуск самого левого свободного элемента
        for i in range(n):
            if not used >> i & 1:
                rec(used | 1 << i, cnt, cur, 0); break
    rec(0, 0, 0, 0)
    return str(best[0])

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
