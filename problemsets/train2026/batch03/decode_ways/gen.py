import random, sys

def gen(n, rnd, k):
    w = [1, 5, 5, 1, 1, 1, 1, 1, 1, 1] if k > 3 else [1] * 10
    s = ''.join(rnd.choices('0123456789', weights=w, k=n))
    if k > 4 and rnd.random() < 0.7:
        s = ''.join(rnd.choice('1112222') + rnd.choice('0123456') for _ in range(n // 2)) or '1'
    return s + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1426 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
