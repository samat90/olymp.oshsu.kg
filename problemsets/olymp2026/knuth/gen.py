"""gen.py n maxA seed"""
import random
import sys

n, A, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
random.seed(s * 3989 + n)
mode = random.random()
if mode < 0.3:
    a = [random.randint(1, A) for _ in range(n)]
elif mode < 0.5:
    a = [random.choice([1, A]) for _ in range(n)]
elif mode < 0.7:  # one heavy piece among light ones
    a = [random.randint(1, max(1, A // 1000)) for _ in range(n)]
    a[random.randrange(n)] = A
else:
    a = sorted(random.randint(1, A) for _ in range(n))
    k = random.randrange(n)
    a = a[k:] + a[:k]
print(n)
print(' '.join(map(str, a)))
