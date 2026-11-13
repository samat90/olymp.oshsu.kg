import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 7 else 'abc'
    s = ''.join(rnd.choice(al) for _ in range(n))
    m = rnd.randint(1, 4 if k == 0 else 300)
    ws = set()
    for _ in range(m):
        ws.add(''.join(rnd.choice(al) for _ in range(rnd.randint(1, 3 if k < 7 else 6))))
    if k > 5:
        ws.add('a')
        ws.add('b')
    ws = sorted(ws)
    return s + '\n' + str(len(ws)) + '\n' + '\n'.join(ws) + '\n'


SIZES = [3, 8, 15, 50, 100, 300, 600, 1000, 1500, 2000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1423 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
