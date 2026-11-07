import sys
from fractions import Fraction

d = sys.stdin.read().split()
n, m = int(d[0]), int(d[1])
E = [(int(d[2 + 3 * i]) - 1, int(d[3 + 3 * i]) - 1, Fraction(int(d[4 + 3 * i]), 100)) for i in range(m)]
res = Fraction(0)
for mask in range(1 << m):
    pr = Fraction(1)
    par = list(range(n))

    def f(x):
        while par[x] != x:
            x = par[x]
        return x
    comps = n
    for i, (u, v, p) in enumerate(E):
        if mask >> i & 1:
            pr *= p
            a, b = f(u), f(v)
            if a != b:
                par[a] = b
                comps -= 1
        else:
            pr *= 1 - p
        if pr == 0:
            break
    if pr and comps == 1:
        res += pr
P = 998244353
print(res.numerator % P * pow(res.denominator % P, P - 2, P) % P)
