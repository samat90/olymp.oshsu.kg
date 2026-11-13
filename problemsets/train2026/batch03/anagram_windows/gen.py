import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 8 else 'abc'
    m = rnd.randint(1, max(1, min(n, 6 if k == 0 else n // 3 + 1)))
    p = [rnd.choice(al) for _ in range(m)]
    s = [rnd.choice(al) for _ in range(n)]
    for _ in range(3):
        if n >= m:
            i = rnd.randrange(n - m + 1)
            q = p[:]
            rnd.shuffle(q)
            s[i:i + m] = q
    return ''.join(s) + '\n' + ''.join(p) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1343 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
