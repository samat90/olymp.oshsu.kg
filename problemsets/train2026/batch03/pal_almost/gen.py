import random, sys

def gen(n, rnd, k):
    al = 'ab' if k == 0 else ('abc' if k < 6 else 'abcdefghijklmnopqrstuvwxyz')
    h = ''.join(rnd.choice(al) for _ in range(max(1, n // 2)))
    s = list(h + rnd.choice(['', 'a']) + h[::-1])
    if rnd.random() < 0.5:
        s.insert(rnd.randrange(len(s) + 1), rnd.choice(al))
    if rnd.random() < 0.3:
        s[rnd.randrange(len(s))] = rnd.choice(al)
    return ''.join(s) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1330 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
