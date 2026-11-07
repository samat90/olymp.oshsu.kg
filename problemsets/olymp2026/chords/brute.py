import sys

d = sys.stdin.read().split()
m = int(d[0])
ch = []
for i in range(m):
    a, b = int(d[1 + 2 * i]), int(d[2 + 2 * i])
    ch.append((min(a, b), max(a, b)))
cnt = 0
for i in range(m):
    a, b = ch[i]
    for j in range(m):
        c, e = ch[j]
        if a < c < b < e:
            cnt += 1
print(1 + m + cnt)
