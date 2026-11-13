import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 5 else 'abcde'
    s = ''.join(rnd.choice(al) for _ in range(n))
    m = min(20000, n)
    ws = []
    tot = 0
    for _ in range(m):
        ln = rnd.randint(1, min(4 if k < 5 else 8, max(1, 100000 // m)))
        ws.append(''.join(rnd.choice(al) for _ in range(ln)))
    return s + '\n' + str(m) + '\n' + '\n'.join(ws) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1368 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
