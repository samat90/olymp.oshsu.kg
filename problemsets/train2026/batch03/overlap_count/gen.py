import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 9 else 'a'
    s = ''.join(rnd.choice(al) for _ in range(n))
    m = rnd.randint(1, max(1, min(n, 3 if k < 5 else 6)))
    return s + '\n' + ''.join(rnd.choice(al) for _ in range(m)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1383 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
