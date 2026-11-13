import random, sys

def gen(n, rnd, k):
    al = 'abc' if k < 6 else 'abcdefghijklmnopqrstuvwxyz'
    s = [rnd.choice(al) for _ in range(n)]
    perm = list('abcdefghijklmnopqrstuvwxyz')
    rnd.shuffle(perm)
    t = [perm[ord(c) - 97] for c in s]
    if rnd.random() < 0.5:
        t[rnd.randrange(n)] = rnd.choice(al)
    return ''.join(s) + '\n' + ''.join(t) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1351 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
