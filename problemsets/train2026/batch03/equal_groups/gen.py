import random, sys

def gen(n, rnd, k):
    s = []
    while len(s) < n:
        s += [rnd.choice('01')] * rnd.randint(1, 4 if k < 8 else 1000)
    return ''.join(s[:n]) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1418 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
