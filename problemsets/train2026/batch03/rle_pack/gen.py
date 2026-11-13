import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 5 else 'abc'
    s = []
    while len(s) < n:
        s += [rnd.choice(al)] * rnd.randint(1, 5 if k < 9 else 1000)
    return ''.join(s[:n]) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1412 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
