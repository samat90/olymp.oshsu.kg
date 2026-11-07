"""gen.py T n mode(rand/graphic/near/dense/sparse) seed
graphic: degrees of a random graph; near: a graphic sequence with one small change."""
import random
import sys

T, N, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 3331 + T)


def graph_degrees(n, m, connected):
    deg = [0] * n
    E = set()
    if connected and n > 1:
        perm = list(range(n))
        random.shuffle(perm)
        for i in range(1, n):
            a, b = perm[i], perm[random.randrange(i)]
            E.add((min(a, b), max(a, b)))
    m = min(m, n * (n - 1) // 2)
    tries = 0
    while len(E) < m and tries < 4 * m + 100:
        tries += 1
        a, b = random.randrange(n), random.randrange(n)
        if a != b:
            E.add((min(a, b), max(a, b)))
    for a, b in E:
        deg[a] += 1
        deg[b] += 1
    return deg


out = []
total = 0
for t in range(T):
    n = N if mode not in ('rand',) else random.randint(1, N)
    if mode == 'rand':
        deg = [random.randint(0, n - 1) for _ in range(n)]
        if random.random() < 0.5 and n > 1:
            deg = [random.randint(0, min(n - 1, 3)) for _ in range(n)]
    else:
        if mode == 'dense':
            m = n * (n - 1) // 2 - random.randint(0, n * 5) if n < 3000 else n * random.randint(5, 15)
        elif mode == 'sparse':
            m = random.randint(n // 2, n + 5)
        else:
            m = random.randint(0, 3 * n)
        deg = graph_degrees(n, m, random.random() < 0.6)
        if mode == 'near' and n > 1:
            r = random.random()
            i = random.randrange(n)
            j = random.randrange(n)
            if r < 0.4:  # move one unit between two vertices: stays even, may break the condition
                if deg[i] > 0 and deg[j] < n - 1 and i != j:
                    deg[i] -= 1
                    deg[j] += 1
                big = max(range(n), key=lambda v: deg[v])
                if deg[big] < n - 1 and deg[j] > 0 and big != j:
                    deg[big] += 1
                    deg[j] -= 1
            elif r < 0.7:
                deg[i] = min(n - 1, deg[i] + 2)
            else:
                k = random.randint(1, max(1, n // 10))
                order = sorted(range(n), key=lambda v: -deg[v])
                for v in order[:k]:
                    deg[v] = min(n - 1, deg[v] + 1)
                for v in order[-k:]:
                    if deg[v] > 0:
                        deg[v] -= 1
    random.shuffle(deg)
    out.append(str(n))
    out.append(' '.join(map(str, deg)))
print(T)
print('\n'.join(out))
