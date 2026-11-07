"""gen.py maxN maxK seed (tests: the numbers themselves; stress: random up to the bounds)"""
import random
import sys

N, K, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
if s >= 100000:  # stress run
    random.seed(s)
    print(random.randint(1, N), random.randint(1, K))
else:
    print(N, K)
