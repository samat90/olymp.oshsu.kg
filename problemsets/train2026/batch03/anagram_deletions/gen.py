import random, sys

def gen(n, rnd, k):
    if k == 0:
        n = min(n, 6)
    al = 'abc' if k == 0 else 'abcdefghij'
    s = ''.join(rnd.choice(al) for _ in range(n))
    m = max(1, n + rnd.randint(-2, 2)) if k == 0 else n
    t = ''.join(rnd.choice(al) for _ in range(m))
    return s + '\n' + t + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1345 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
