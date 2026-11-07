import sys

d = sys.stdin.read().split()
B, n, q = int(d[0]), int(d[1]), int(d[2])
a = [int(x) for x in d[3:3 + n]]
cnt = {}
for mask in range(1, 1 << n):
    v = (1 << B) - 1
    for i in range(n):
        if mask >> i & 1:
            v &= a[i]
    cnt[v] = cnt.get(v, 0) + 1
print('\n'.join(str(cnt.get(int(x), 0) % 1000000007) for x in d[3 + n:3 + n + q]))
