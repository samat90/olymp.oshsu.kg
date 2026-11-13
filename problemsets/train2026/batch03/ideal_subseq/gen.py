import random, sys

def gen(n, rnd, k):
    if k == 0:
        n = min(n, 11)
    kk = rnd.randint(0, 3 if k < 7 else 25)
    return str(kk) + '\n' + ''.join(rnd.choice('abcdefghijklmnopqrstuvwxyz' if k > 4 else 'abcdefg') for _ in range(n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1427 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
