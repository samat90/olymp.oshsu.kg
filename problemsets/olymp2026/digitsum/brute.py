import sys

d = sys.stdin.read().split()
T = int(d[0])
out = []
for t in range(T):
    l, r = int(d[1 + 2 * t]), int(d[2 + 2 * t])
    out.append(sum(1 for x in range(l, r + 1) if x % sum(map(int, str(x))) == 0))
print('\n'.join(map(str, out)))
