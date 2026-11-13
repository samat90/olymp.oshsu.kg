import random, sys

def gen(n, rnd, k):
    r = rnd.randint(1, 6 if k < 7 else 1000)
    return str(r) + '\n' + ''.join(rnd.choice('abcdefXYZ') for _ in range(n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1409 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
