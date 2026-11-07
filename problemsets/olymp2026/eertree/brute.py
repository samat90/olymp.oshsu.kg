import sys

s = sys.stdin.read().split()[0]
n = len(s)
occ = {}
for i in range(n):
    for j in range(i + 1, n + 1):
        t = s[i:j]
        if t == t[::-1]:
            occ[t] = occ.get(t, 0) + 1
print(len(occ), max(len(t) * c for t, c in occ.items()))
