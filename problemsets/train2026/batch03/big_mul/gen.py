import random, sys

def gen(n, rnd, k):
    def num(m):
        return rnd.choice('123456789') + ''.join(rnd.choice('0123456789') for _ in range(m - 1)) if m > 1 else rnd.choice('0123456789')
    return num(n) + '\n' + num(max(1, n + rnd.randint(-2, 2))) + '\n'


SIZES = [3, 8, 15, 50, 100, 300, 500, 800, 1000, 1000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1405 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
