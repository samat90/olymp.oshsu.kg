"""gen.py T maxC seed"""
import random
import sys

T, C, s = (int(x) for x in sys.argv[1:4])
random.seed(s * 1777 + T)
out = []
for _ in range(T):
    c = random.randint(1, C) if random.random() < 0.5 else random.randint(C // 2, C)
    r = random.random()
    if r < 0.3:
        a, b = random.randint(1, 100), random.randint(1, 100)
    elif r < 0.6:
        a, b = random.randint(1, max(1, c // 2)), random.randint(1, max(1, c // 2))
    elif r < 0.8:  # nearly equal prices, close to the golden ratio: many Euclid steps
        f1, f2 = 1, 1
        while f2 < c // 100 and f2 < 10 ** 9 // 2:
            f1, f2 = f2, f1 + f2
        a, b = f2, f1
    else:
        a, b = random.randint(1, 10 ** 9), random.randint(1, 10 ** 9)
    if C <= 10 ** 5 and a * 1 + b > c and random.random() < 0.8:
        a, b = random.randint(1, max(1, c // 3)), random.randint(1, max(1, c // 3))
    if random.random() < 0.5:
        a, b = b, a
    out.append('%d %d %d' % (a, b, c))
print(T)
print('\n'.join(out))
