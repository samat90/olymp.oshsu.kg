"""gen.py T maxR seed"""
import random
import sys

T, R, s = (int(x) for x in sys.argv[1:4])
random.seed(s * 8191 + T)
out = []
for i in range(T):
    if R <= 10 ** 6:
        l = random.randint(1, R)
        r = random.randint(l, min(R, l + random.randint(0, 3 * 10 ** 5)))
    else:
        l = random.randint(1, R) if random.random() < 0.7 else random.randint(1, 1000)
        r = random.randint(l, R)
        if random.random() < 0.3:
            r = R
    out.append('%d %d' % (l, r))
print(T)
print('\n'.join(out))
