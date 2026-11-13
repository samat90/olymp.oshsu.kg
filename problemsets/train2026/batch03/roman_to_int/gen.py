import random, sys

def gen(n, rnd, k):
    def rom(x):
        t = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
             (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
        r = ''
        for v, s in t:
            while x >= v:
                r += s
                x -= v
        return r
    q = min(n, 3999)
    xs = rnd.sample(range(1, 4000), q)
    return str(q) + '\n' + '\n'.join(rom(x) for x in xs) + '\n'


SIZES = [3, 8, 15, 100, 400, 1000, 2000, 3000, 3999, 3999]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1402 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
