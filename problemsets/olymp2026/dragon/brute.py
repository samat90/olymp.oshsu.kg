import sys

d = sys.stdin.buffer.read().split()
q = int(d[0])
Ns = [int(v) for v in d[1:1 + q]]
M = max(Ns)
x = y = 0
dx, dy = 1, 0
pts = [(0, 0)]
for n in range(1, M + 1):
    x += dx
    y += dy
    pts.append((x, y))
    m = n
    while m % 2 == 0:
        m //= 2
    if ((m - 1) // 2) % 2 == 0:
        dx, dy = -dy, dx
    else:
        dx, dy = dy, -dx
print('\n'.join('%d %d' % pts[N] for N in Ns))
