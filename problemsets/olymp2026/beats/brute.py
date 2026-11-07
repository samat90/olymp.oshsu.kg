import sys

d = sys.stdin.read().split()
n, q = int(d[0]), int(d[1])
a = [int(x) for x in d[2:2 + n]]
pos = 2 + n
out = []
for _ in range(q):
    t, l, r = int(d[pos]), int(d[pos + 1]) - 1, int(d[pos + 2])
    pos += 3
    if t == 1:
        x = int(d[pos])
        pos += 1
        for i in range(l, r):
            if a[i] > x:
                a[i] = x
    elif t == 2:
        x = int(d[pos])
        pos += 1
        for i in range(l, r):
            a[i] += x
    elif t == 3:
        out.append(sum(a[l:r]))
    else:
        out.append(max(a[l:r]))
print('\n'.join(map(str, out)))
