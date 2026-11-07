"""gen.py T maxM mode(rand/prime/nocoprime/solvable/pow2/smooth) seed"""
import random
import sys

T, M, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 6007 + T)


def is_prime(v):
    if v < 2:
        return False
    i = 2
    while i * i <= v:
        if v % i == 0:
            return False
        i += 1
    return True


out = []
for _ in range(T):
    if mode == 'prime':
        m = random.randint(M // 2, M)
        while not is_prime(m):
            m -= 1
    elif mode == 'pow2':
        m = 1 << random.randint(1, M.bit_length() - 1)
    elif mode == 'smooth':
        m = 1
        while True:
            p = random.choice([2, 3, 5, 7, 11, 13, 17])
            if m * p > M:
                break
            m *= p
    elif mode == 'nocoprime':
        g = random.choice([2, 3, 4, 6, 8, 12, 30])
        m = random.randint(1, max(1, M // g)) * g
    else:
        m = random.randint(1, M)
    a = random.randint(0, 10 ** 9 if M > 10 ** 6 else 3 * m)
    if mode in ('nocoprime', 'pow2', 'smooth') and random.random() < 0.7:
        a = random.choice([2, 4, 6, 12, 30, 10, 18]) * random.randint(1, 1000)
    if mode == 'solvable' or random.random() < 0.6:  # b = a^x for a large hidden x
        x = random.randint(0, m if m > 1 else 5)
        b = pow(a, x, m)
        if random.random() < 0.3:
            b += m * random.randint(0, (10 ** 9 - b) // m)
    else:
        b = random.randint(0, min(10 ** 9, 3 * m))
    out.append('%d %d %d' % (a, b, m))
print(T)
print('\n'.join(out))
