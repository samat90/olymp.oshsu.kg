"""gen.py q maxN maxLen seed: half of the patterns are taken from the sequence itself"""
import random
import sys

q, M, ML, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
random.seed(s * 4242 + q)


def t(i):
    return bin(i).count('1') & 1


out = []
for _ in range(q):
    if random.random() < 0.3:
        b = random.randint(0, M.bit_length() - 1)
        N = (1 << b) + random.randint(-ML, ML)
    else:
        N = random.randint(1, M)
    N = min(M, max(1, N))
    L = random.randint(1, ML)
    if random.random() < 0.65:
        start = random.randint(0, max(0, min(N, 10 ** 17) - 1))
        if random.random() < 0.4:
            start = (1 << random.randint(0, 59)) - random.randint(0, L)
            start = max(0, start)
        pat = ''.join(str(t(start + x)) for x in range(L))
    else:
        pat = ''.join(random.choice('01') for _ in range(L))
    out.append('%d %s' % (N, pat))
print(q)
print('\n'.join(out))
