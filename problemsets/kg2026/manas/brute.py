import sys

d = sys.stdin.read().split()
n, q, s = int(d[0]), int(d[1]), d[2]
subs = sorted(set(s[i:j] for i in range(n) for j in range(i + 1, n + 1)))
out = []
for i in range(q):
    k = int(d[3 + i])
    if k > len(subs):
        out.append('-1')
    else:
        t = subs[k - 1]
        p = s.find(t)
        out.append('%d %d' % (p + 1, p + len(t)))
print('\n'.join(out))
