"""gen.py n shape seed  (shapes from genlib.tree)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, tree, write  # noqa: E402

n, shape, s = int(sys.argv[1]), sys.argv[2], sys.argv[3]
seed(s)
write([str(n)] + ['%d %d' % e for e in tree(n, shape)])
