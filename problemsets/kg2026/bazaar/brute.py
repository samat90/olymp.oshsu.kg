import sys
d = sys.stdin.buffer.read().split()
n, q = int(d[0]), int(d[1])
a = [0] + [int(x) for x in d[2:2 + n]]
p = 2 + n
out = []
for _ in range(q):
    t, l, r = int(d[p]), int(d[p + 1]), int(d[p + 2])
    p += 3
    if t == 3:
        seg = a[l:r + 1]
        out.append('%d %d' % (sum(seg), max(seg)))
    else:
        x = int(d[p]); p += 1
        for i in range(l, r + 1):
            a[i] = a[i] + x if t == 1 else x
print('\n'.join(out))
