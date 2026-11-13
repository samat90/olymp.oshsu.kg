import random, sys

def gen(n, rnd, k):
    n = max(2, n - n % 2)
    pr = rnd.choice([0.5, 0.6])
    out = []
    o = 0
    for i in range(n):
        left = n - i
        if o == left:
            out.append(')')
            o -= 1
        elif o == 0 or rnd.random() < pr:
            out.append('(')
            o += 1
        else:
            out.append(')')
            o -= 1
    return ''.join(out) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1393 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
