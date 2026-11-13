import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n = t[0]
    tasks = sorted((t[1 + 2 * i], t[2 + 2 * i], i) for i in range(n)); h = []; i = 0; now = 0; res = []
    while len(res) < n:
        if not h and now < tasks[i][0]: now = tasks[i][0]
        while i < n and tasks[i][0] <= now:
            heapq.heappush(h, (tasks[i][1], tasks[i][2])); i += 1
        d, j = heapq.heappop(h); now += d; res.append(j + 1)
    return ' '.join(map(str, res))

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
