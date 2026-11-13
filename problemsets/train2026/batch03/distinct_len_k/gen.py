import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 8 else 'abc'
    kk = rnd.randint(1, n) if k < 8 else rnd.choice([n // 2, 17, 5, n - 3, 1])
    kk = max(1, min(n, kk))
    return str(kk) + '\n' + ''.join(rnd.choice(al) for _ in range(n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1387 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
