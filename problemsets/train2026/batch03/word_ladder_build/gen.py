import random, sys

def gen(n, rnd, k):
    words = set()
    al = 'ab'
    tries = 0
    while len(words) < n and tries < n * 5:
        tries += 1
        if words and rnd.random() < 0.7:
            w = rnd.choice(sorted(words)) if len(words) < 50 else rnd.choice(list(words))
            if len(w) < 12:
                words.add(w + rnd.choice(al))
                continue
        words.add(''.join(rnd.choice(al) for _ in range(rnd.randint(1, 8))))
    ws = sorted(words)
    rnd.shuffle(ws)
    return str(len(ws)) + '\n' + ' '.join(ws) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1415 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
