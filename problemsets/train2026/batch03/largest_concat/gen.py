import random, sys

def gen(n, rnd, k):
    if k == 0:
        n = min(n, 6)
    xs = []
    for _ in range(n):
        r = rnd.random()
        if r < 0.3:
            xs.append(rnd.randint(0, 99))
        elif r < 0.6:
            xs.append(rnd.choice([3, 30, 34, 5, 50, 505, 9, 90, 909, 1, 10, 100]))
        else:
            xs.append(rnd.randint(0, 10 ** 9))
    return str(n) + '\n' + ' '.join(map(str, xs)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 10000, 20000, 50000, 50000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1422 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
