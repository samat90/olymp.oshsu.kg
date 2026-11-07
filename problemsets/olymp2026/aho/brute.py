import sys
from itertools import product

d = sys.stdin.read().split()
sigma, k, L = int(d[0]), int(d[1]), int(d[2])
words = d[3:3 + k]
letters = 'abcdefghijklmnopqrstuvwxyz'[:sigma]
cnt = 0
for t in product(letters, repeat=L):
    s = ''.join(t)
    if not any(w in s for w in words):
        cnt += 1
print(cnt % 1000000007)
