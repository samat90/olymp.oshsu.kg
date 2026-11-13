import random, sys

def gen(n, rnd, k):
    pool = ['osh', 'naryn', 'talas', 'batken', 'karakol', 'tokmok', 'kant', 'kara', 'balykchy', 'kerben']
    m = 3 if k == 0 else (4 + k)
    ws = []
    for _ in range(n):
        if rnd.random() < 0.7:
            ws.append(pool[rnd.randrange(min(m, 10))])
        else:
            ws.append(''.join(rnd.choice('abc') for _ in range(rnd.randint(1, 3))))
    return str(n) + '\n' + ' '.join(ws) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1347 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
