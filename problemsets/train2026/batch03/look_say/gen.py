import random, sys

def gen(n, rnd, k):
    if k == 0:
        n = min(n, 12)
    return str(n) + '\n'


SIZES = [1, 2, 3, 5, 8, 12, 20, 30, 36, 40]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1411 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
