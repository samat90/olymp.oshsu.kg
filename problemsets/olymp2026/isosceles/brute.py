import sys

d = sys.stdin.read().split()
n = int(d[0])
p = [(int(d[1 + 2 * i]), int(d[2 + 2 * i])) for i in range(n)]


def d2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


cnt = 0
for i in range(n):
    for j in range(i + 1, n):
        for k in range(j + 1, n):
            a, b, c = p[i], p[j], p[k]
            if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) == 0:
                continue
            x, y, z = d2(a, b), d2(b, c), d2(a, c)
            if x == y or y == z or x == z:
                cnt += 1
print(cnt)
