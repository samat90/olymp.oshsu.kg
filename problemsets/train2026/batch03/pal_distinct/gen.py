import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 8 else 'abc'
    if k == 10:
        return ''.join(rnd.choice('ab') for _ in range(n // 2)) * 2 + '\n'
    return ''.join(rnd.choice(al) for _ in range(n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1337 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
