import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 8 else 'abc'
    s = ''.join(rnd.choice(al) for _ in range(n))
    sh = rnd.randrange(n)
    t = s[sh:] + s[:sh]
    if rnd.random() < 0.3:
        t = list(t)
        t[rnd.randrange(n)] = rnd.choice(al)
        t = ''.join(t)
    return s + '\n' + t + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1380 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
