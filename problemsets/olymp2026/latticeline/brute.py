import sys

d = sys.stdin.read().split()
T = int(d[0])
out = []
for t in range(T):
    a, b, c = int(d[1 + 3 * t]), int(d[2 + 3 * t]), int(d[3 + 3 * t])
    cnt = 0
    x = 1
    while a * x + b <= c:
        cnt += (c - a * x) // b
        x += 1
    out.append(cnt)
print('\n'.join(map(str, out)))
