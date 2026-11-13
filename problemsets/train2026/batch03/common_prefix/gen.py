import random, sys

def gen(n, rnd, k):
    base = ''.join(rnd.choice('ab') for _ in range(rnd.randint(0, min(5 if k < 8 else 100, max(1, 250000 // n - 3)))))
    ws = []
    for _ in range(n):
        ws.append(base + ''.join(rnd.choice('ab') for _ in range(rnd.randint(0 if base else 1, 2 if k < 8 else 1))))
    return str(n) + '\n' + '\n'.join(ws) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1366 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
