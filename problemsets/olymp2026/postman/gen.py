"""gen.py n m maxW seed: connected multigraph with at most 20 odd vertices"""
import random
import sys

n, m, W, s = (int(x) for x in sys.argv[1:5])
random.seed(s * 1597 + n)
target = max(n - 1, m - n // 2)
perm = list(range(1, n + 1))
random.shuffle(perm)
E = []
for i in range(1, n):  # spanning tree
    E.append((perm[i], perm[random.randrange(max(0, i - 30), i)] if random.random() < 0.7 else perm[random.randrange(i)]))
while len(E) < target:
    if random.random() < 0.03:
        v = random.randint(1, n)
        E.append((v, v))
    else:
        a, b = random.randint(1, n), random.randint(1, n)
        E.append((a, b))
deg = [0] * (n + 1)
for a, b in E:
    deg[a] += 1
    deg[b] += 1
odd = [v for v in range(1, n + 1) if deg[v] % 2]
random.shuffle(odd)
keep = random.choice([0, 2, 4, 8, 12, 16, 20])
while len(odd) > keep:  # pair up odd vertices with extra streets
    a, b = odd.pop(), odd.pop()
    E.append((a, b))
random.shuffle(E)
print(n, len(E))
print('\n'.join('%d %d %d' % (a, b, random.randint(1, W)) for a, b in E))
