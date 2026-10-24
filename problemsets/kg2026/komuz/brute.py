import sys
d = sys.stdin.read().split()
n = int(d[0]); s = d[1:1 + n]
seen = set()
out = []
for i in range(n):
    for j in range(i + 1):
        seen.add(tuple(s[j:i + 1]))
    out.append(str(len(seen)))
print('\n'.join(out))
