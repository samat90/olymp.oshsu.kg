import random, sys

def gen(n, rnd, k):
    al = 'ab'
    divs = [d for d in range(1, n + 1) if n % d == 0]
    d = rnd.choice(divs)
    base = ''.join(rnd.choice(al) for _ in range(d))
    s = base * (n // d)
    if k > 5 and n > 1 and rnd.random() < 0.3:
        h = ''.join(rnd.choice(al) for _ in range(max(1, n // 12)))
        s = (h * (n // len(h) + 1))[:n]
        if n % len(h):
            s = s[:-1] + 'b'
    return s + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1377 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
