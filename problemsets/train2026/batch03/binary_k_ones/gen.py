import random, sys

def gen(n, rnd, k):
    p = rnd.choice([0.1, 0.3, 0.5, 0.8])
    s = ''.join('1' if rnd.random() < p else '0' for _ in range(n))
    kk = rnd.randint(0, 3 if k < 5 else max(1, int(n * p / 3)))
    return str(kk) + '\n' + s + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1363 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
