import sys

s = sys.stdin.read().split()[0]
n = len(s)
rots = [s[i:] + s[:i] for i in range(n)]
best = min(rots)
first = rots.index(best) + 1
distinct = len(set(rots))


def is_lyndon(w):
    return all(w < w[i:] + w[:i] for i in range(1, len(w)))


# greedy: the longest Lyndon prefix each time gives the factorisation
k, i = 0, 0
while i < n:
    j = n
    while not is_lyndon(s[i:j]):
        j -= 1
    k += 1
    i = j
print(first, distinct, k)
