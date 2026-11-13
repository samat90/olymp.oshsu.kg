import random, sys

def gen(n, rnd, k):
    p = rnd.choice([0.5, 0.55, 0.45])
    return ''.join('(' if rnd.random() < p else ')' for _ in range(n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1392 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
