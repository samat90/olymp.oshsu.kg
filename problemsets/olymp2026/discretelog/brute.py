import sys

d = sys.stdin.read().split()
T = int(d[0])
out = []
for t in range(T):
    a, b, m = int(d[1 + 3 * t]), int(d[2 + 3 * t]), int(d[3 + 3 * t])
    ans = -1
    cur = 1 % m
    for x in range(2 * m + 70):
        if cur == b % m:
            ans = x
            break
        cur = cur * a % m
    out.append(ans)
print('\n'.join(map(str, out)))
