import sys

d = sys.stdin.read().split()
n = int(d[0])
p = [(int(d[1 + 2 * i]), int(d[2 + 2 * i])) for i in range(n)]


def cr(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


O = (0, 0)
cnt = 0
for i in range(n):
    for j in range(i + 1, n):
        for k in range(j + 1, n):
            a, b, c = p[i], p[j], p[k]
            s1, s2, s3 = cr(a, b, O), cr(b, c, O), cr(c, a, O)
            if (s1 > 0 and s2 > 0 and s3 > 0) or (s1 < 0 and s2 < 0 and s3 < 0):
                cnt += 1
print(cnt)
