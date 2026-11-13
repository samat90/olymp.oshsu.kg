import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    lines = s.split('\n'); q = int(lines[0]); d = deque(); out = []
    for i in range(1, q + 1):
        p = lines[i].split(); c = p[0]
        if c == 'push_front': d.appendleft(p[1])
        elif c == 'push_back': d.append(p[1])
        elif c == 'size': out.append(str(len(d)))
        elif not d: out.append('ERROR')
        elif c == 'pop_front': out.append(d.popleft())
        elif c == 'pop_back': out.append(d.pop())
        elif c == 'front': out.append(d[0])
        else: out.append(d[-1])
    return '\n'.join(out)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
