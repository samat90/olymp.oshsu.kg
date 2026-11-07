import sys

d = sys.stdin.read().split()
n = int(d[0])
p = [(int(d[1 + 2 * i]), int(d[2 + 2 * i])) for i in range(n)]
best, cnt = -1, 0
for i in range(n):
    for j in range(i + 1, n):
        v = (p[i][0] - p[j][0]) ** 2 + (p[i][1] - p[j][1]) ** 2
        if v > best:
            best, cnt = v, 1
        elif v == best:
            cnt += 1
print(best, cnt)
