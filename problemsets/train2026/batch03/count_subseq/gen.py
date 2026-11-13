import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 8 else 'abc'
    s = ''.join(rnd.choice(al) for _ in range(n))
    m = rnd.randint(1, max(1, min(n, 4 if k == 0 else n // 2 + 1)))
    t = ''.join(rnd.choice(al) for _ in range(m))
    return s + '\n' + t + '\n'


SIZES = [3, 8, 15, 50, 100, 300, 600, 1000, 1500, 1500]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1370 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
