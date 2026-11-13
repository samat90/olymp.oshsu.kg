import random, sys

def gen(n, rnd, k):
    out = []
    for _ in range(n):
        x = rnd.randint(1, 800 if k == 0 else rnd.choice([30, 800, 18000, 2147483647]))
        if rnd.random() < 0.5:
            out.append(str(x))
        else:
            t = ''
            while x:
                x -= 1
                t = chr(65 + x % 26) + t
                x //= 26
            out.append(t)
    return str(n) + '\n' + '\n'.join(out) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1410 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
