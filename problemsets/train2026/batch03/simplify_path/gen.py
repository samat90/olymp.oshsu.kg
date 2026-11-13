import random, sys

def gen(n, rnd, k):
    parts = []
    L = 1
    while L < n:
        p = rnd.choice(['a', 'b', 'osh', '.', '..', '..', '...', 'x.y', '', 'c1'])
        parts.append(p)
        L += len(p) + 1
    s = '/' + '/'.join(parts)
    if rnd.random() < 0.5:
        s += '/'
    return s + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1408 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
