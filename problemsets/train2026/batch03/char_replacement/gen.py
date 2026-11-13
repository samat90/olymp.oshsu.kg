import random, sys

def gen(n, rnd, k):
    al = 'AB' if k < 5 else 'ABCDE'
    kk = rnd.randint(0, 3 if k < 7 else n // 3 + 1)
    return str(kk) + '\n' + ''.join(rnd.choice(al) for _ in range(n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1357 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
