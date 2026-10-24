import sys

d = sys.stdin.read().split()
n, W, V = int(d[0]), int(d[1]), int(d[2])
items = [(int(d[3 + 2 * i]), int(d[4 + 2 * i])) for i in range(n)]
sums = [(0, 0)]
for w, v in items:
    sums += [(a + w, b + v) for a, b in sums]
print(sum(1 for a, b in sums if a <= W and b >= V))
