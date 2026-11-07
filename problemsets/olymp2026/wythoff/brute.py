import sys

d = sys.stdin.read().split()
T = int(d[0])
qs = [(int(d[1 + 2 * i]), int(d[2 + 2 * i])) for i in range(T)]
M = max(max(a, b) for a, b in qs) + 1
win = [[False] * M for _ in range(M)]
for a in range(M):
    for b in range(M):
        w = False
        for x in range(a):
            if not win[x][b]:
                w = True
                break
        if not w:
            for y in range(b):
                if not win[a][y]:
                    w = True
                    break
        if not w:
            for t in range(1, min(a, b) + 1):
                if not win[a - t][b - t]:
                    w = True
                    break
        win[a][b] = w
out = []
for a, b in qs:
    c = sum(1 for x in range(a) if not win[x][b]) + sum(1 for y in range(b) if not win[a][y])
    c += sum(1 for t in range(1, min(a, b) + 1) if not win[a - t][b - t])
    out.append(c)
print('\n'.join(map(str, out)))
