import inspect, os, json, random, time, sys, textwrap
import re
import sys, random
from math import *
from itertools import *
from functools import *
from collections import *
from bisect import *
import heapq
from fractions import Fraction
import builtins
pow = builtins.pow
PRE = """import sys, random
from math import *
from itertools import *
from functools import *
from collections import *
from bisect import *
import heapq
from fractions import Fraction
import builtins, re
pow = builtins.pow
sys.setrecursionlimit(1000000)
def mat_text(a): return "\\n".join(" ".join(map(str, r)) for r in a)
"""
TASKS = []
def N(r, t, tiny, big):
    if t == 0: return r.randint(1, tiny)
    if t == 10: return big
    if t <= 3: return r.randint(1, tiny * 2)
    return max(1, big * t * t // 100)
def T(code, name, topic, tl, stmt, samples):
    def deco(cls):
        TASKS.append(dict(code=code, name=name, topic=topic, tl=tl, stmt=stmt.strip(), samples=samples, cls=cls))
        return cls
    return deco
def src(f, newname):
    s = textwrap.dedent(inspect.getsource(f))
    lines = s.split("\n")
    while lines[0].lstrip().startswith("@"): lines.pop(0)
    # drop decorator-free; rename def
    lines[0] = lines[0].replace("def " + f.__name__, "def " + newname, 1)
    return "\n".join(lines)
def norm(o):
    return "\n".join(l.rstrip() for l in str(o).strip().split("\n"))

N_SRC = """def N(r, t, tiny, big):
    if t == 0: return r.randint(1, tiny)
    if t == 10: return big
    if t <= 3: return r.randint(1, tiny * 2)
    return max(1, big * t * t // 100)
"""
