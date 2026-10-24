"""gen.py t mode(small/rand/prime/semiprime/composite/pdiv/pow/mixed) seed"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, write  # noqa: E402

P = 10 ** 9 + 7
LIM = 10 ** 18
SMALL = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
t, mode, s = int(sys.argv[1]), sys.argv[2], sys.argv[3]
seed(s)


def is_prime(n):
    if n < 2:
        return False
    for p in SMALL:
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in SMALL:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def prime_near(x):
    while not is_prime(x):
        x += 1
    return x


# numbers with very many divisors (up to 103680 for 897612484786617600)
HIGHLY = [897612484786617600, 748010403988848000, 963761198400, 866421317361600, 321253732800,
          720720, 735134400, 551350800, 4497552259200, 18401055938125660800 // 20 // 2]


def pick_n(kind):
    if kind == 'small':
        return random.randint(3, 9)
    if kind == 'rand':
        return random.randint(3, LIM)
    if kind == 'prime':
        return prime_near(random.randint(LIM // 2, LIM - 10 ** 6))
    if kind == 'semiprime':
        a = prime_near(random.randint(10 ** 8, 10 ** 9))
        b = prime_near(random.randint(10 ** 8, LIM // a - 10 ** 3))
        return a * b
    if kind == 'composite':
        x = random.choice(HIGHLY)
        return x if 3 <= x <= LIM else 720720
    if kind == 'pdiv':
        return P * random.randint(1, LIM // P)
    if kind == 'pow':
        return random.choice([2 ** 59, 3 ** 37, 2 ** 30 * 3 ** 18, 5 ** 25, P * 2 ** 29, 7 ** 21, P * 3 ** 18])
    return random.randint(3, 100)


def pick_k():
    if mode == 'small':
        return random.randint(1, 4)
    if random.random() < 0.5:
        return random.randint(1, LIM)
    return random.choice([1, 2, 3, P, P + 1, P + 2, 2 * P + 1, LIM, random.randint(1, 100)])


kinds = ['rand', 'semiprime', 'composite', 'pdiv', 'prime', 'pow', 'tiny']
lines = [str(t)]
for _ in range(t):
    kind = mode if mode != 'mixed' else random.choice(kinds)
    lines.append('%d %d' % (pick_n(kind), pick_k()))
write(lines)
