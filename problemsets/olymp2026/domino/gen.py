"""gen.py n m seed"""
import random
import sys

n, m, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
if s >= 100000:  # stress: all sizes up to the bounds
    random.seed(s)
    n, m = random.randint(1, n), random.randint(1, m)
print(n, m)
