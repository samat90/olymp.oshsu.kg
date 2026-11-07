import sys

d = sys.stdin.read().split()
T = int(d[0])
out = []
for t in range(T):
    a, m = int(d[1 + 2 * t]), int(d[2 + 2 * t])
    out.append(sum(1 for x in range(m) if x * x % m == a))
print('\n'.join(map(str, out)))
