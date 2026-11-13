import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 8 else 'abc'
    s = ''.join(rnd.choice(al) for _ in range(n))
    m = rnd.randint(1, max(1, min(n, 3 if k < 5 else 2000 if k > 8 else 200)))
    p = ''.join(rnd.choice(al + '??') for _ in range(m))
    return s + '\n' + p + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1385 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
