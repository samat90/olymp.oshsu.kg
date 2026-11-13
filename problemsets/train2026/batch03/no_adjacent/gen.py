import random, sys

def gen(n, rnd, k):
    if k == 0:
        n = min(n, 9)
    m = rnd.randint(1, 4 if k < 8 else 26)
    al = 'abcdefghijklmnopqrstuvwxyz'[:m]
    s = [rnd.choice(al) for _ in range(n)]
    if rnd.random() < 0.5:
        c = (n + 1) // 2 + rnd.randint(-1, 1)
        for i in range(max(0, min(n, c))):
            s[i] = 'z'
        rnd.shuffle(s)
    return ''.join(s) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1349 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
