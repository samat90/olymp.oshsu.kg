import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    s = s.split()[0]; n = len(s); cnt = Counter(s)
    if max(cnt.values()) > (n + 1) // 2: return 'НЕТ'
    res = []; last = ''
    for pos in range(n):
        m = n - pos - 1
        for c in sorted(cnt):
            if cnt[c] == 0 or c == last: continue
            cnt[c] -= 1
            ok = all(v <= (m + 1) // 2 for v in cnt.values()) and cnt[c] <= m // 2
            if ok: res.append(c); last = c; break
            cnt[c] += 1
    return ''.join(res)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
