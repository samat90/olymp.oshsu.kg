import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    s = s.split()[0]; pos = [0]
    def parse():
        cnt = Counter()
        while pos[0] < len(s) and s[pos[0]] != ')':
            if s[pos[0]] == '(':
                pos[0] += 1; sub = parse(); pos[0] += 1
                m = num()
                for e, v in sub.items(): cnt[e] += v * m
            else:
                e = s[pos[0]]; pos[0] += 1
                while pos[0] < len(s) and s[pos[0]].islower(): e += s[pos[0]]; pos[0] += 1
                cnt[e] += num()
        return cnt
    def num():
        m = ''
        while pos[0] < len(s) and s[pos[0]].isdigit(): m += s[pos[0]]; pos[0] += 1
        return int(m) if m else 1
    cnt = parse()
    return ''.join(e + (str(cnt[e]) if cnt[e] > 1 else '') for e in sorted(cnt))

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
