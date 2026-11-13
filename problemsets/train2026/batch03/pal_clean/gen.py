import random, sys

def gen(n, rnd, k):
    al = 'ab' if k == 0 else 'abcxyzABC0189'
    h = ''.join(rnd.choice(al) for _ in range(max(1, n // 2)))
    s = list(h + rnd.choice(['', 'a', 'Z']) + h[::-1])
    if rnd.random() < 0.5:
        s[rnd.randrange(len(s))] = rnd.choice(al)
    out = []
    for c in s:
        while rnd.random() < 0.3:
            out.append(rnd.choice(' ,.:!-'))
        out.append(c.swapcase() if rnd.random() < 0.4 else c)
    r = ''.join(out).strip()
    return (r if any(c.isalnum() for c in r) else 'a') + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1329 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
