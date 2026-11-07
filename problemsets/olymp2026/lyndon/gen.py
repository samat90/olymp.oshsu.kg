"""gen.py n sigma seed"""
import random
import sys

n, sigma, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
random.seed(s * 919 + n)
letters = 'abcdefghijklmnopqrstuvwxyz'[:sigma]
mode = random.choice(['rand', 'period', 'nearperiod', 'sorted', 'lyndonpow'])
if mode == 'period':
    p = ''.join(random.choice(letters) for _ in range(random.randint(1, 10)))
    t = (p * (n // len(p) + 1))[:n]
    if random.random() < 0.5 and n % len(p) == 0:
        pass
elif mode == 'nearperiod':
    p = ''.join(random.choice(letters) for _ in range(random.randint(1, 10)))
    t = list((p * (n // len(p) + 1))[:n])
    t[random.randrange(n)] = random.choice(letters)
    t = ''.join(t)
elif mode == 'sorted':  # descending blocks: many Lyndon factors
    t = ''.join(sorted((random.choice(letters) for _ in range(n)), reverse=random.random() < 0.7))
elif mode == 'lyndonpow':
    w = 'a' + ''.join(random.choice(letters) for _ in range(random.randint(0, 8)))
    t = (w * (n // len(w) + 1))[:n]
    t = t[n // 3:] + t[:n // 3]
else:
    t = ''.join(random.choice(letters) for _ in range(n))
print(t)
