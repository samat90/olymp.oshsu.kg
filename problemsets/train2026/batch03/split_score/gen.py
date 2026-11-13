import random, sys

def gen(n, rnd, k):
    n = max(2, n)
    return ''.join(rnd.choice('01') for _ in range(n)) + '\n'


SIZES = [2, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1419 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
