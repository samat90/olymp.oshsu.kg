import random, sys

def gen(n, rnd, k):
    if k == 0:
        n = min(n, 10)
    w = rnd.choice([(3, 3, 4), (1, 1, 8), (4, 2, 2)])
    return ''.join(rnd.choices('()?', weights=w, k=n)) + '\n'


SIZES = [3, 8, 15, 30, 60, 150, 300, 500, 800, 1000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1400 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
