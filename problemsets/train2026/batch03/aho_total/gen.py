import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 8 else 'abc'
    s = ''.join(rnd.choice(al) for _ in range(n))
    m = max(1, min(50000, n if k else 4))
    mx = max(1, min(6, 100000 // m))
    ws = [''.join(rnd.choice(al) for _ in range(rnd.randint(1, mx))) for _ in range(m)]
    return s + '\n' + str(m) + '\n' + '\n'.join(ws) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1372 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
