import sys
from fractions import Fraction

d = sys.stdin.read().split()
n = int(d[0])
p = [Fraction(int(x), 100) for x in d[1:1 + n]]
E = [(int(d[1 + n + 2 * i]) - 1, int(d[2 + n + 2 * i]) - 1) for i in range(n - 1)]
res = Fraction(0)
for mask in range(1 << n):
    pr = Fraction(1)
    for i in range(n):
        pr *= p[i] if mask >> i & 1 else 1 - p[i]
    if pr == 0:
        continue
    par = list(range(n))

    def f(x):
        while par[x] != x:
            x = par[x]
        return x
    c = bin(mask).count('1')
    for a, b in E:
        if mask >> a & 1 and mask >> b & 1:
            par[f(a)] = f(b)
            c -= 1
    res += pr * c * c
P = 998244353
print(res.numerator % P * pow(res.denominator % P, P - 2, P) % P)
