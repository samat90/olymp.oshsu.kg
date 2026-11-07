"""gen.py n maxW shape seed"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, tree  # noqa: E402

n, W, shape, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
seed(s)
print(n)
print('\n'.join('%d %d %d' % (a, b, random.randint(1, W)) for a, b in tree(n, shape)))
