import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 8 else 'abc'
    p = rnd.randint(1, max(1, min(n, 4 if k < 6 else n // 3 + 1)))
    base = ''.join(rnd.choice(al) for _ in range(p))
    s = (base * (n // p + 1))[:n]
    if rnd.random() < 0.3:
        s = s[:-1] + rnd.choice(al)
    return s + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1376 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
