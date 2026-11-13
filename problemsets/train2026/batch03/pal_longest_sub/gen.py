import random, sys

def gen(n, rnd, k):
    al = 'ab' if (k == 0 or k < 7) else 'abc'
    s = ''.join(rnd.choice(al) for _ in range(n))
    if k >= 5:
        h = ''.join(rnd.choice(al) for _ in range(n // 3))
        p = rnd.randrange(0, n - len(h) * 2 + 1) if n - len(h) * 2 > 0 else 0
        s = (s[:p] + h + h[::-1] + s[p + 2 * len(h):])[:n]
    return s + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1331 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
