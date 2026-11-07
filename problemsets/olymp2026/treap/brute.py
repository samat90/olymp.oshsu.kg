import sys

d = sys.stdin.read().split()
n, q = int(d[0]), int(d[1])
a = [int(x) for x in d[2:2 + n]]
pos = 2 + n
out = []
for _ in range(q):
    t = int(d[pos])
    if t in (1, 4, 5):
        l, r = int(d[pos + 1]), int(d[pos + 2])
        pos += 3
        if t == 1:
            a[l - 1:r] = a[l - 1:r][::-1]
        elif t == 4:
            out.append(sum(a[l - 1:r]))
        else:
            out.append(max(a[l - 1:r]))
    elif t == 2:
        p, x = int(d[pos + 1]), int(d[pos + 2])
        pos += 3
        a.insert(p, x)
    else:
        p = int(d[pos + 1])
        pos += 2
        a.pop(p - 1)
print('\n'.join(map(str, out)))
