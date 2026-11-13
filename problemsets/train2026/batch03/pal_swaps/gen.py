import random, sys

def gen(n, rnd, k):
    al = 'ab' if k == 0 else ('abc' if k < 6 else 'abcdefghij')
    h = [rnd.choice(al) for _ in range(n // 2)]
    s = h + h[:]
    if n % 2:
        s.append(rnd.choice(al))
    rnd.shuffle(s)
    return ''.join(s) + '\n'


SIZES = [3, 8, 15, 50, 100, 300, 800, 1500, 2000, 2000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1340 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
