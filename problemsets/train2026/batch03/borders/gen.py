import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 8 else 'abc'
    if k > 5:
        h = ''.join(rnd.choice(al) for _ in range(max(1, n // 6)))
        mid = ''.join(rnd.choice(al) for _ in range(max(0, n - 2 * len(h))))
        return (h + mid + h)[:max(n, 1)] + '\n'
    return ''.join(rnd.choice(al) for _ in range(n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1378 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
