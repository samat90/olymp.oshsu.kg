import random, sys

def gen(n, rnd, k):
    if k == 0:
        n = min(n, 8)
    C = [1]
    for i in range(1, n + 1):
        C.append(C[-1] * 2 * (2 * i - 1) // (i + 1))
    total = C[n]
    r = rnd.random()
    if r < 0.1:
        kk = total + rnd.randint(1, 3)
    elif r < 0.2:
        kk = total
    else:
        kk = rnd.randint(1, total)
    kk = min(kk, 10 ** 16)
    return '%d %d\n' % (n, kk)


SIZES = [1, 2, 3, 5, 8, 12, 18, 24, 28, 30]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1401 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
