import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 7 else 'abc'
    a = ''.join(rnd.choice(al) for _ in range(n))
    b = ''.join(rnd.choice(al) for _ in range(max(1, n + rnd.randint(-1, 1))))
    i = j = 0
    c = []
    while i < len(a) or j < len(b):
        if j == len(b) or (i < len(a) and rnd.random() < 0.5):
            c.append(a[i])
            i += 1
        else:
            c.append(b[j])
            j += 1
    if rnd.random() < 0.4:
        c[rnd.randrange(len(c))] = rnd.choice(al)
    elif rnd.random() < 0.3:
        rnd.shuffle(c)
    return a + '\n' + b + '\n' + ''.join(c) + '\n'


SIZES = [2, 4, 7, 20, 50, 100, 200, 300, 400, 500]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1424 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
