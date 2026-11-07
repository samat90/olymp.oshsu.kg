import sys

d = sys.stdin.read().split()
N, M, A, B = int(d[0]), int(d[1]), int(d[2]), int(d[3])
g = d[4:4 + N]
p = d[4 + N:4 + N + A]


def rot(q):
    r, c = len(q), len(q[0])
    return [''.join(q[r - 1 - i][j] for i in range(r)) for j in range(c)]


rs = [p]
for _ in range(3):
    rs.append(rot(rs[-1]))
seen = set()
for q in rs:
    r, c = len(q), len(q[0])
    for i in range(N - r + 1):
        for j in range(M - c + 1):
            if all(g[i + a][j:j + c] == q[a] for a in range(r)):
                seen.add((i, j, r, c))
print(len(seen))
