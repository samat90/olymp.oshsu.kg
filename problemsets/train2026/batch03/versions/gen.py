import random, sys

def gen(n, rnd, k):
    def ver(m):
        return '.'.join(('0' * rnd.randint(0, 2)) + str(rnd.choice([0, 1, 2, 10, rnd.randint(0, 10 ** 9)]) if k > 5 else rnd.randint(0, 2)) for _ in range(m))
    m = max(1, n)
    a = ver(m)
    parts = a.split('.')
    r = rnd.random()
    if r < 0.3:
        b = a + '.0' * rnd.randint(0, 3)
    elif r < 0.6:
        b = '.'.join(parts[:-1] + [str(int(parts[-1]) + rnd.choice([-1, 1, 0]) if int(parts[-1]) > 0 else 1)])
    else:
        b = ver(max(1, m + rnd.randint(-2, 2)))
    return a + '\n' + b + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1407 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
