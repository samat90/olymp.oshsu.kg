"""gen.py q maxN mode(rand/pow/alt/all) seed"""
import random
import sys

q, M, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 31337 + q)
out = []
for i in range(q):
    if mode == 'all':
        v = i * (M // q)
    elif mode == 'pow':  # near powers of two and their sums: the turning points of the recursion
        b = random.randint(0, max(0, M.bit_length() - 1))
        v = (1 << b) + random.randint(-3, 3)
        if random.random() < 0.5:
            v += 1 << random.randint(0, b)
    elif mode == 'alt':  # alternating bit patterns 1010..., 1100...
        b = random.randint(1, M.bit_length())
        pat = random.choice(['10', '01', '110', '1001', '1'])
        v = int((pat * 64)[:b], 2) + random.randint(-2, 2)
    else:
        v = random.randint(0, M)
    out.append(min(M, max(0, v)))
print(q)
print('\n'.join(map(str, out)))
