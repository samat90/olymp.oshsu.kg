import random, sys

def gen(n, rnd, k):
    w = [3, 3, rnd.choice([0, 1, 3])]
    return ''.join(rnd.choices('abc', weights=w, k=n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1361 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
