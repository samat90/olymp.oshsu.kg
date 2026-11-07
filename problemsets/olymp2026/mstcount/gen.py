"""gen.py n m wmax mode(rand/split/clusters/complete) seed"""
import random
import sys

n, m, W, mode, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
random.seed(s * 101 + n)
edges = []
perm = list(range(1, n + 1))
random.shuffle(perm)
if mode == 'split':  # two halves with no edge between them: no system exists
    h = max(1, n // 2)
    A, B = perm[:h], perm[h:] or perm[:1]
    while len(edges) < m:
        part = A if random.random() < 0.5 or len(B) < 2 else B
        if len(part) < 2:
            part = A if len(A) >= 2 else B
        a, b = random.sample(part, 2)
        edges.append((a, b, random.randint(1, W)))
elif mode == 'clusters':  # dense groups joined by a few heavier edges: many ties inside the groups
    k = random.randint(5, 20)
    grp = [perm[i::k] for i in range(k)]
    for i in range(1, k):
        a, b = random.choice(grp[i - 1]), random.choice(grp[i])
        edges.append((a, b, W + 1))
    while len(edges) < m:
        if random.random() < 0.05:
            a, b = random.sample(perm, 2)
            edges.append((a, b, random.randint(W, W + 2)))
        else:
            g = random.choice(grp)
            if len(g) < 2:
                continue
            a, b = random.sample(g, 2)
            edges.append((a, b, random.randint(1, W)))
elif mode == 'complete':
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((perm[i], perm[j], random.randint(1, W)))
    random.shuffle(edges)
    edges = edges[:m]
else:
    for i in range(1, n):  # random tree keeps the graph connected
        edges.append((perm[random.randrange(i)], perm[i], random.randint(1, W)))
    while len(edges) < m:
        a, b = random.sample(perm, 2)
        edges.append((a, b, random.randint(1, W)))
random.shuffle(edges)
edges = edges[:m]
print(n, len(edges))
print('\n'.join('%d %d %d' % e for e in edges))
