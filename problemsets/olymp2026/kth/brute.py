import sys

d = sys.stdin.read().split()
n, q = int(d[0]), int(d[1])
a = [int(x) for x in d[2:2 + n]]
pos = 2 + n
last = 0
out = []
for _ in range(q):
    x, y, z = int(d[pos]), int(d[pos + 1]), int(d[pos + 2])
    pos += 3
    l = ((x ^ last) % n) + 1
    r = ((y ^ last) % n) + 1
    if l > r:
        l, r = r, l
    k = ((z ^ last) % (r - l + 1)) + 1
    last = sorted(a[l - 1:r])[k - 1]
    out.append(last)
print('\n'.join(map(str, out)))
