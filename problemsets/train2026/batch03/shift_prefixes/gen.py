import random, sys

def gen(n, rnd, k):
    s = ''.join(rnd.choice('abcxyz') for _ in range(n))
    return s + '\n' + ' '.join(str(rnd.randint(0, 10 ** 9)) for _ in range(n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1413 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
