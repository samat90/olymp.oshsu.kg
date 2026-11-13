import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 9 else 'a'
    if k > 5:
        p = max(1, n // rnd.randint(1, 4))
        base = ''.join(rnd.choice(al) for _ in range(p))
        s = (base * (n // p + 1))[:n]
        return s + '\n'
    return ''.join(rnd.choice(al) for _ in range(n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1381 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
