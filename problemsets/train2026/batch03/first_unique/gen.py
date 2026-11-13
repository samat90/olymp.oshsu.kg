import random, sys

def gen(n, rnd, k):
    al = 'abc' if k == 0 else ('abcdefghijklmnopqrstuvwxyz' if k < 5 else 'abcdefghijklmnopqrstuvwxyz'[:rnd.randint(1, 26)])
    s = [rnd.choice(al) for _ in range(n)]
    if k > 6:
        h = ''.join(rnd.choice('abcdefghijklm') for _ in range(n // 2))
        s = list(h + h)
        if rnd.random() < 0.7 and s:
            s[rnd.randrange(len(s))] = 'z'
    return ''.join(s) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1346 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
