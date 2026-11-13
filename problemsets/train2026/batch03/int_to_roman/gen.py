import random, sys

def gen(n, rnd, k):
    q = min(n, 3999)
    return str(q) + '\n' + '\n'.join(str(x) for x in rnd.sample(range(1, 4000), q)) + '\n'


SIZES = [3, 8, 15, 100, 400, 1000, 2000, 3000, 3999, 3999]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1403 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
