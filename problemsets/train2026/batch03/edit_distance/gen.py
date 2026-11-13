import random, sys

def gen(n, rnd, k):
    if k == 0:
        n = min(n, 6)
    al = 'ab' if k < 6 else 'abcdef'
    a = ''.join(rnd.choice(al) for _ in range(n))
    b = list(a)
    for _ in range(rnd.randint(0, 3 if k else 2)):
        r = rnd.random()
        if r < 0.3 and b:
            b.pop(rnd.randrange(len(b)))
        elif r < 0.6:
            b.insert(rnd.randint(0, len(b)), rnd.choice(al))
        elif b:
            b[rnd.randrange(len(b))] = rnd.choice(al)
    if rnd.random() < 0.3 or not b:
        b = [rnd.choice(al) for _ in range(max(1, n))]
    return a + '\n' + ''.join(b) + '\n'


SIZES = [3, 8, 15, 50, 100, 200, 400, 600, 800, 800]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1371 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
