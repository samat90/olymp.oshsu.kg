import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 6 else 'abcdefghijklmnopqrstuvwxyz'
    s = ''.join(rnd.choice(al) for _ in range(n))
    if k > 6 and n > 20:
        L = n // 5
        i = rnd.randrange(n - L)
        j = rnd.randrange(n - L)
        if abs(i - j) > L:
            s = s[:j] + s[i:i + L] + s[j + L:]
    return s + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1388 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
