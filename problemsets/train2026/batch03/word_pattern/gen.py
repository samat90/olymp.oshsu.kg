import random, sys

def gen(n, rnd, k):
    al = 'abc' if k < 6 else 'abcdefghijklmnopqrstuvwxyz'
    p = [rnd.choice(al) for _ in range(n)]
    names = {}
    for c in 'abcdefghijklmnopqrstuvwxyz':
        names[c] = ''.join(rnd.choice('xyz') for _ in range(6)) + c
    ws = [names[c] for c in p]
    if rnd.random() < 0.5:
        i = rnd.randrange(n)
        ws[i] = names[rnd.choice(al)]
    if rnd.random() < 0.2:
        j = rnd.randrange(n)
        ws[j] = 'q'
    return ''.join(p) + '\n' + ' '.join(ws) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 10000, 20000, 50000, 50000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1353 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
