import sys
d = sys.stdin.read().split()
n, q = int(d[0]), int(d[1])
busy = [False] * (n + 1)
p = 2
out = []
def seats(l, r):
    return list(range(l, r + 1)) if l <= r else list(range(l, n + 1)) + list(range(1, r + 1))
for _ in range(q):
    c = d[p]; p += 1
    if c == '+':
        k = int(d[p]); p += 1
        s = 0
        if k <= n:
            for st in range(1, n + 1):
                if all(not busy[(st - 1 + i) % n + 1] for i in range(k)):
                    s = st
                    break
        if s:
            for i in range(k):
                busy[(s - 1 + i) % n + 1] = True
        out.append(str(s))
    else:
        l, r = int(d[p]), int(d[p + 1]); p += 2
        if c == '-':
            for x in seats(l, r):
                busy[x] = False
        else:
            out.append(str(sum(1 for x in seats(l, r) if not busy[x])))
print('\n'.join(out))
