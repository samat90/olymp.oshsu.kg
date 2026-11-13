import random, sys

def gen(n, rnd, k):
    al = 'abc' if k == 0 else 'abcdefghijklmnopqrstuvwxyz'
    g = [rnd.choice(al) for _ in range(n + rnd.randint(0, n // 5 + 2))]
    z = g[:]
    rnd.shuffle(z)
    note = z[:n]
    if rnd.random() < 0.5:
        note[rnd.randrange(n)] = rnd.choice(al)
    return ''.join(note) + '\n' + ''.join(g) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1352 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
