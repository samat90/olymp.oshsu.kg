import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 8 else 'abc'
    s = ''
    while len(s) < n:
        h = ''.join(rnd.choice(al) for _ in range(rnd.randint(1, 4)))
        s += h + h[::-1] if rnd.random() < 0.6 else h
    s = s[:n]
    q = n if k else 5
    q = min(q, 100000)
    lines = [s, str(q)]
    for _ in range(q):
        if rnd.random() < 0.5:
            c = rnd.randrange(n)
            d = rnd.randint(0, min(c, n - 1 - c, 6))
            l, r = c - d, c + d
        else:
            l = rnd.randrange(n)
            r = rnd.randrange(l, n)
        lines.append('%d %d' % (l + 1, r + 1))
    return '\n'.join(lines) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1341 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
