"""gen.py n sigma seed: random, periodic and palindrome-rich strings"""
import random
import sys

n, sigma, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
random.seed(s * 101 + n)
letters = 'abcdefghijklmnopqrstuvwxyz'[:sigma]
mode = random.choice(['rand', 'period', 'fib', 'pal', 'blocks'])
if mode == 'period':
    p = ''.join(random.choice(letters) for _ in range(random.randint(1, 7)))
    t = (p * (n // len(p) + 1))[:n]
elif mode == 'fib':  # Fibonacci words have many palindromes
    a, b = 'a', 'ab' if sigma > 1 else 'aa'
    while len(b) < n:
        a, b = b, b + a
    off = random.randint(0, len(b) - n)
    t = b[off:off + n]
    if sigma > 1 and random.random() < 0.5:
        t = t.translate(str.maketrans('ab', ''.join(random.sample(letters, 2))))
elif mode == 'pal':
    parts = []
    while sum(map(len, parts)) < n:
        h = ''.join(random.choice(letters) for _ in range(random.randint(1, 20)))
        parts.append(h + random.choice(['', random.choice(letters)]) + h[::-1])
    t = ''.join(parts)[:n]
elif mode == 'blocks':
    t = ''.join(random.choice(letters) * random.randint(1, 30) for _ in range(n))[:n]
else:
    t = ''.join(random.choice(letters) for _ in range(n))
print(t)
