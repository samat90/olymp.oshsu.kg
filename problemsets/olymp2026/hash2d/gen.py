"""gen.py N M A B sigma seed: pattern copies (in all rotations) are planted into the grid"""
import random
import sys

N, M, A, B, sigma, s = (int(x) for x in sys.argv[1:7])
random.seed(s * 3037 + N * 7 + A)
letters = 'abcdefghijklmnopqrstuvwxyz'[:sigma]
mode = random.random()
if mode < 0.3:  # periodic pattern and grid: many overlapping matches
    per = [''.join(random.choice(letters) for _ in range(random.randint(1, 3))) for _ in range(random.randint(1, 3))]
    g = [list((per[i % len(per)] * (M // len(per[i % len(per)]) + 2))[:M]) for i in range(N)]
    pat = [''.join(g[(i + 1) % N][j] for j in range(min(B, M))) for i in range(min(A, N))]
    pat = [(row * (B // len(row) + 1))[:B] for row in pat]
    while len(pat) < A:
        pat.append(pat[len(pat) % len(pat)])
else:
    g = [[random.choice(letters) for _ in range(M)] for _ in range(N)]
    pat = [''.join(random.choice(letters) for _ in range(B)) for _ in range(A)]


def rot(q):
    r, c = len(q), len(q[0])
    return [''.join(q[r - 1 - i][j] for i in range(r)) for j in range(c)]


rs = [pat]
for _ in range(3):
    rs.append(rot(rs[-1]))
for _ in range(random.randint(1, 40)):
    q = random.choice(rs)
    r, c = len(q), len(q[0])
    if r > N or c > M:
        continue
    i, j = random.randint(0, N - r), random.randint(0, M - c)
    for a in range(r):
        for b in range(c):
            g[i + a][j + b] = q[a][b]
print(N, M, A, B)
print('\n'.join(''.join(row) for row in g))
print('\n'.join(pat))
