"""gen.py T maxN maxK seed"""
import random
import sys

T, N, K, s = (int(x) for x in sys.argv[1:5])
random.seed(s * 541 + T)
out = []
for i in range(T):
    n = random.randint(1, N) if random.random() < 0.6 else random.randint(N // 2, N)
    k = random.randint(1, K) if random.random() < 0.6 else K
    if i == 0:
        n, k = N, K
    out.append('%d %d' % (n, k))
print(T)
print('\n'.join(out))
