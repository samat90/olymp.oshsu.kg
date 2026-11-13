import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 4 else 'abcde'
    return ''.join(rnd.choice(al) for _ in range(n)) + '\n'


SIZES = [3, 8, 15, 50, 100, 300, 500, 800, 1000, 1000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1335 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
