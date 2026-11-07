import sys


def d2xy(n, d):
    x = y = 0
    s = 1
    while s < n:
        rx = 1 & (d // 2)
        ry = 1 & (d ^ rx)
        if ry == 0:
            if rx == 1:
                x, y = s - 1 - x, s - 1 - y
            x, y = y, x
        x += s * rx
        y += s * ry
        d //= 4
        s *= 2
    return x, y


d = sys.stdin.read().split()
k, q = int(d[0]), int(d[1])
n = 1 << k
num = [[0] * n for _ in range(n)]
for i in range(n * n):
    x, y = d2xy(n, i)
    num[x][y] = i
out = []
for t in range(q):
    x1, y1, x2, y2 = map(int, d[2 + 4 * t:6 + 4 * t])
    vals = [num[x][y] for x in range(x1, x2 + 1) for y in range(y1, y2 + 1)]
    out.append('%d %d' % (min(vals), max(vals)))
print('\n'.join(out))
