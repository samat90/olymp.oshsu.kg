import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 5 else 'abcde'
    n = min(n, 10) if k == 0 else n
    a = ''.join(rnd.choice(al) for _ in range(n))
    b = ''.join(rnd.choice(al) for _ in range(max(1, n + rnd.randint(-2, 2))))
    return a + '\n' + b + '\n'


SIZES = [3, 8, 15, 50, 100, 300, 500, 800, 1000, 1000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1367 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
