"""gen.py T maxN seed"""
import random
import sys

T, M, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
random.seed(s * 997 + M)
ns = [random.randint(2, M) for _ in range(T)]
if M > 100:
    ns[0] = M
    ns[-1] = random.randint(2, 20)
print(T)
print('\n'.join(map(str, ns)))
