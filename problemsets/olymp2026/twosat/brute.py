import sys

d = sys.stdin.read().split()
n, m = int(d[0]), int(d[1])
C = [tuple(int(x) for x in d[2 + 4 * k:6 + 4 * k]) for k in range(m)]
for mask in range(1 << n):
    s = [(mask >> (n - 1 - i)) & 1 for i in range(n)]
    if all(s[i - 1] == x or s[j - 1] == y for i, x, j, y in C):
        print(''.join(map(str, s)))
        break
else:
    print('NO')
