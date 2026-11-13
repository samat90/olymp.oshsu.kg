import random, sys

def gen(n, rnd, k):
    s = []
    while len(s) < n:
        m = rnd.randint(1, 8 if k < 7 else 3000)
        a0 = rnd.randint(0, 20)
        al = 'abcdefghijklmnopqrstuvwxyz'[a0:a0 + rnd.randint(1, 5)]
        s += [rnd.choice(al) for _ in range(m)]
    return ''.join(s[:n]) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1420 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
