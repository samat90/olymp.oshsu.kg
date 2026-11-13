import random, sys

def gen(n, rnd, k):
    al = 'abc' if k == 0 else 'abcdefg'
    ws = []
    for _ in range(n):
        ln = rnd.randint(1, 4 if k == 0 else 6)
        ws.append(''.join(rnd.choice(al) for _ in range(ln)))
    return str(n) + '\n' + ' '.join(ws) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 10000, 20000, 50000, 50000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1344 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
