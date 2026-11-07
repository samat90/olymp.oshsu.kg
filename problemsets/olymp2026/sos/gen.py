"""gen.py B n q seed: masks with many common bits so that the AND is rarely zero"""
import random
import sys

B, n, q, s = (int(x) for x in sys.argv[1:5])
random.seed(s * 263 + n)
S = 1 << B
mode = random.random()
if mode < 0.4:
    dens = random.uniform(0.6, 0.95)
    a = [sum(1 << b for b in range(B) if random.random() < dens) for _ in range(n)]
elif mode < 0.7:
    base = [random.randrange(S) | random.randrange(S) for _ in range(5)]
    a = [random.choice(base) | (random.randrange(S) & random.randrange(S)) for _ in range(n)]
else:
    a = [random.randrange(S) for _ in range(n)]
xs = []
for _ in range(q):
    if random.random() < 0.6:  # the AND of a few random masks: usually a non-zero answer
        v = S - 1
        for _ in range(random.randint(1, 4)):
            v &= random.choice(a)
        xs.append(v)
    else:
        xs.append(random.randrange(S))
print(B, n, q)
print(' '.join(map(str, a)))
print(' '.join(map(str, xs)))
