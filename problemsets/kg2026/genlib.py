"""Shared helpers for the test generators."""
import random
import sys


def seed(value):
    random.seed(int(value) * 1000003 + 7)


def tree(n, shape, shuffle=True):
    """Return n-1 edges (1-based) of a tree of the given shape."""
    if shape == 'pathfixed':  # 1 - 2 - 3 - ... - n, no relabelling
        return [(i, i + 1) for i in range(1, n)]
    par = [0] * n
    for i in range(1, n):
        if shape == 'path':
            p = i - 1
        elif shape == 'star':
            p = 0
        elif shape == 'binary':
            p = (i - 1) // 2
        elif shape == 'caterpillar':
            p = i - 1 if i < n // 2 else random.randrange(n // 2)
        elif shape == 'deep':
            p = max(0, i - random.randint(1, 3))
        elif shape == 'broom':
            p = i - 1 if i < 2 * n // 3 else 2 * n // 3 - 1
        elif shape == 'sqrt':
            k = max(1, int(n ** 0.5))
            p = i - 1 if i % k else max(0, i - k)
        else:  # random
            p = random.randrange(i)
        par[i] = p
    perm = list(range(1, n + 1))
    if shuffle:
        random.shuffle(perm)
    edges = [(perm[par[i]], perm[i]) for i in range(1, n)]
    if shuffle:
        random.shuffle(edges)
        edges = [(a, b) if random.random() < 0.5 else (b, a) for a, b in edges]
    return edges


def write(lines):
    out = sys.stdout
    out.write('\n'.join(lines))
    out.write('\n')
