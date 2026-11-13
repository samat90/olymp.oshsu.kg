import random, sys

def gen(n, rnd, k):
    al = 'abc' if k < 6 else 'abcdefgh'
    m = rnd.randint(1, 4 if k < 6 else max(2, min(n // 3, 20)))
    t = ''.join(rnd.choice(al) for _ in range(m))
    s = ''.join(rnd.choice(al) for _ in range(n))
    if k > 6 and rnd.random() < 0.8:
        q = list(s)
        for c in t:
            q[rnd.randrange(n)] = c
        s = ''.join(q)
    return s + '\n' + t + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1358 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
