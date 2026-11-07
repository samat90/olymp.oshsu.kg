import sys

d = sys.stdin.read().split()
q = int(d[0])
qs = [(int(d[1 + 2 * i]), d[2 + 2 * i]) for i in range(q)]
M = max(n for n, _ in qs)
t = ''.join(str(bin(i).count('1') & 1) for i in range(M))
out = []
for n, s in qs:
    pre = t[:n]
    c, i = 0, pre.find(s)
    while i != -1:
        c += 1
        i = pre.find(s, i + 1)
    out.append(c)
print('\n'.join(map(str, out)))
