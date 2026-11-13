import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 4 else 'abc'
    if k > 7:
        h = ''.join(rnd.choice('ab') for _ in range(rnd.randint(1, 3)))
        s = ''
        while len(s) < n:
            s += h + h[::-1] if rnd.random() < 0.5 else h
        return s[:n] + '\n'
    return ''.join(rnd.choice(al) for _ in range(n)) + '\n'


SIZES = [3, 8, 15, 50, 100, 300, 500, 800, 1000, 1000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1336 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
