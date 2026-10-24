# Literal simulation: stones are sown one by one (small counts only).
import sys

d = sys.stdin.read().split()
n = int(d[0])
N = 2 * n
a = [int(x) for x in d[1:1 + N]]
m = int(d[1 + N])
moves = [int(x) for x in d[2 + N:2 + N + m]]
kazan = [0, 0]
tuz = [None, None]
owner = {}
for t, j in enumerate(moves):
    p = t % 2
    h = p * n + j - 1
    if h in owner or a[h] == 0:
        continue
    c = a[h]
    a[h] = 0
    pos = h if c > 1 else (h + 1) % N
    last = pos
    for k in range(c):
        if pos in owner:
            kazan[owner[pos]] += 1
        else:
            a[pos] += 1
        last = pos
        pos = (pos + 1) % N
    if last // n != p and last not in owner:
        if a[last] % 2 == 0:
            kazan[p] += a[last]
            a[last] = 0
        elif a[last] == 3 and tuz[p] is None and last % n != n - 1 and \
                not (tuz[1 - p] is not None and tuz[1 - p] % n == last % n):
            tuz[p] = last
            owner[last] = p
            kazan[p] += 3
            a[last] = 0
print(kazan[0], kazan[1])
print(0 if tuz[0] is None else tuz[0] + 1, 0 if tuz[1] is None else tuz[1] + 1)
print(' '.join(map(str, a)))
