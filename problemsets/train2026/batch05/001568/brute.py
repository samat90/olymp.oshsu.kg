import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def brute(s):
    lines = s.split('\n'); q = int(lines[0]); a = []; out = []
    for i in range(1, q + 1):
        p = lines[i].split(); c = p[0]
        if c == 'push_front': a.insert(0, p[1])
        elif c == 'push_back': a += [p[1]]
        elif c == 'size': out.append(str(len(a)))
        elif len(a) == 0: out.append('ERROR')
        elif c == 'pop_front': out.append(a.pop(0))
        elif c == 'pop_back': out.append(a.pop())
        elif c == 'front': out.append(a[0])
        else: out.append(a[len(a) - 1])
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()).strip() + "\n")
