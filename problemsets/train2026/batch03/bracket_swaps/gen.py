import random, sys

def gen(n, rnd, k):
    n = max(2, n - n % 2)
    s = ['['] * (n // 2) + [']'] * (n // 2)
    rnd.shuffle(s)
    return ''.join(s) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1399 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
