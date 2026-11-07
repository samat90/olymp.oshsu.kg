import sys

d = sys.stdin.buffer.read().split()
k, q = int(d[0]), int(d[1])
n = 3 ** k


def filled(x, y):
    while x or y:
        if x % 3 == 1 and y % 3 == 1:
            return 0
        x //= 3
        y //= 3
    return 1


P = [[0] * (n + 1) for _ in range(n + 1)]
for i in range(n):
    s = 0
    for j in range(n):
        s += filled(i, j)
        P[i + 1][j + 1] = P[i][j + 1] + s
out = []
for t in range(q):
    x1, y1, x2, y2 = map(int, d[2 + 4 * t:6 + 4 * t])
    out.append(P[x2 + 1][y2 + 1] - P[x1][y2 + 1] - P[x2 + 1][y1] + P[x1][y1])
print('\n'.join(map(str, out)))
