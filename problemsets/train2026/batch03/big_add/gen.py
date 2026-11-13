import random, sys

def gen(n, rnd, k):
    def num(m):
        return rnd.choice('123456789') + ''.join(rnd.choice('0123456789') for _ in range(m - 1)) if m > 1 else rnd.choice('0123456789')
    if rnd.random() < 0.15:
        return '9' * n + '\n' + rnd.choice(['1', '9' * rnd.randint(1, n)]) + '\n'
    return num(n) + '\n' + num(rnd.randint(1, n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1404 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
