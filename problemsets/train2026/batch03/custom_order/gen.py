import random, sys

def gen(n, rnd, k):
    letters = list('abcdefghijklmnopqrstuvwxyz')
    rnd.shuffle(letters)
    order = ''.join(letters[:rnd.randint(1, 26 if k else 5)])
    al = 'abcdef' if k == 0 else 'abcdefghijklmnopqrstuvwxyz'
    return order + '\n' + ''.join(rnd.choice(al) for _ in range(n)) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1354 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
