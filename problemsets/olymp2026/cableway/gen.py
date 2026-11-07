"""gen.py n maxX maxS mode(rand/dense/clusters) seed"""
import random
import sys

n, X, S, mode, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
random.seed(s * 31 + n)
if mode == 'dense':
    xs = sorted(random.sample(range(min(X, 10 ** 7) + 1), n)) if X >= n else list(range(n))
elif mode == 'clusters':
    k = random.randint(5, 50)
    centers = sorted(random.sample(range(X + 1), k))
    pts = set()
    while len(pts) < n:
        c = random.choice(centers)
        pts.add(min(X, max(0, c + random.randint(-X // (10 * k) - 1, X // (10 * k) + 1))))
    xs = sorted(pts)
else:
    xs = sorted(random.sample(range(X + 1), n))
L = (xs[-1] - xs[0]) ** 2
cap = max(0, min(S, (4 * 10 ** 18 - L) // n))
ss = [random.randint(0, cap) if random.random() < 0.8 else random.choice([0, cap]) for _ in range(n)]
print(n)
print(' '.join(map(str, xs)))
print(' '.join(map(str, ss)))
