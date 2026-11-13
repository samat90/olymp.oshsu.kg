import random, sys

def gen(n, rnd, k):
    out = []
    for _ in range(n):
        s = ' ' * rnd.randint(0, 3)
        s += rnd.choice(['', '', '+', '-', '--', '+-'])
        s += ''.join(rnd.choice('0123456789') for _ in range(rnd.choice([0, 1, 3, 9, 10, 12, 20])))
        s += rnd.choice(['', ' x', 'abc', '.5', ' 12', '-3'])
        if not s.strip():
            s = 'q'
        out.append(s)
    return str(n) + '\n' + '\n'.join(out) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1414 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
