import random, sys

def gen(n, rnd, k):
    if k == 0:
        n = min(n, 11)
    al = 'abc' if k == 0 else 'abcdefghijklmnopqrstuvwxyz'
    w = [rnd.random() ** 2 for _ in al]
    return ''.join(rnd.choices(al, weights=w, k=n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1348 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
