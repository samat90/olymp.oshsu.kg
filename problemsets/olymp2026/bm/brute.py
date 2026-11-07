# Find the shortest recurrence by Gaussian elimination for every order, then iterate up to N.
import sys

P = 998244353
d = sys.stdin.read().split()
k, N = int(d[0]), int(d[1])
a = [int(x) for x in d[2:2 + 2 * k]]


def solve(L):
    # equations a[i] = sum c_j a[i-j], i = L .. 2k-1
    rows = [[a[i - j] for j in range(1, L + 1)] + [a[i]] for i in range(L, 2 * k)]
    m = len(rows)
    r = 0
    where = [-1] * L
    for col in range(L):
        piv = next((i for i in range(r, m) if rows[i][col] % P), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = pow(rows[r][col], P - 2, P)
        rows[r] = [x * inv % P for x in rows[r]]
        for i in range(m):
            if i != r and rows[i][col]:
                f = rows[i][col]
                rows[i] = [(x - f * y) % P for x, y in zip(rows[i], rows[r])]
        where[col] = r
        r += 1
    for i in range(r, m):
        if rows[i][L] % P:
            return None
    return [rows[where[j]][L] if where[j] >= 0 else 0 for j in range(L)]


for L in range(0, k + 1):
    c = solve(L)
    if c is not None:
        break
seq = a[:]
while len(seq) <= N:
    i = len(seq)
    seq.append(sum(c[j] * seq[i - 1 - j] for j in range(L)) % P)
print(seq[N])
