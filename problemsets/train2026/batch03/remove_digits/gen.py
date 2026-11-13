import random, sys

def gen(n, rnd, k):
    s = ''.join(rnd.choice('0123456789' if k > 3 else '0123') for _ in range(n))
    kk = rnd.randint(0, n)
    if k > 4 and rnd.random() < 0.5:
        kk = rnd.randint(0, n // 2)
    return str(kk) + '\n' + s + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1421 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
