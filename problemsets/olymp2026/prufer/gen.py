"""gen.py T maxN seed"""
import random
import sys

T, M, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
random.seed(s * 2221 + M)
out = []
for _ in range(T):
    n = random.randint(max(2, M // 2), M) if M > 10 else random.randint(2, M)
    r = random.random()
    if r < 0.5:  # typical trees: about n/e leaves, small degree of vertex 1
        c = max(1, min(n, int(n / 2.718) + random.randint(-n // 50 - 2, n // 50 + 2)))
        d = random.randint(1, min(n - 1, 6))
    elif r < 0.8:
        c = random.randint(1, n)
        d = random.randint(1, n - 1)
    else:
        c = random.choice([2, n - 1, n, 1, 3])
        c = max(1, min(n, c))
        d = random.choice([1, 2, n - 1, n - c + 1 if n - c + 1 >= 1 else 1])
        d = max(1, min(n - 1, d))
    out.append('%d %d %d' % (n, c, d))
print(T)
print('\n'.join(out))
