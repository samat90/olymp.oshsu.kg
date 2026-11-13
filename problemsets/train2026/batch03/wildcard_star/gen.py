import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 6 else 'abc'
    s = ''.join(rnd.choice(al) for _ in range(n))
    m = rnd.randint(1, max(1, n // 2 + 1))
    if rnd.random() < 0.6:
        p = []
        for c in s:
            r = rnd.random()
            if r < 0.2:
                p.append('*')
            elif r < 0.4:
                p.append('?')
            elif r < 0.8:
                p.append(c)
        p = ''.join(p) or '*'
        p = p.replace('**', '*')
    else:
        p = ''.join(rnd.choice(al + '??*') for _ in range(m))
    return s + '\n' + p + '\n'


SIZES = [3, 8, 15, 50, 100, 300, 500, 800, 1000, 1000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1384 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
