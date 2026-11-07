import sys
from fractions import Fraction

d = sys.stdin.read().split()
T = int(d[0])
P = 998244353
out = []
for t in range(T):
    a, b, x, y = (int(v) for v in d[1 + 4 * t:5 + 4 * t])
    N = a + b
    p = Fraction(x, y)
    q = 1 - p
    # E[i] = 1 + p E[i+1] + q E[i-1], E[0] = E[N] = 0: write E[i] = c[i] + k[i] * E[1]
    c, k = [Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]
    for i in range(1, N):
        c.append((c[i] - 1 - q * c[i - 1]) / p)
        k.append((k[i] - q * k[i - 1]) / p)
    e1 = -c[N] / k[N]
    e = c[a] + k[a] * e1
    out.append(e.numerator % P * pow(e.denominator % P, P - 2, P) % P)
print('\n'.join(map(str, out)))
