import random, sys

def gen(n, rnd, k):
    p = rnd.choice([0.5, 0.2, 0.8])
    return ''.join('1' if rnd.random() < p else '0' for _ in range(n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1416 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
