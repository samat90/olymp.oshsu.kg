import random, sys

def gen(n, rnd, k):
    if k == 0:
        n = min(n, 6)
    r = rnd.random()
    if r < 0.15:
        return '9' * n + '\n'
    s = rnd.choice('123456789') + ''.join(rnd.choice('0123456789' if r < 0.6 else '9') for _ in range(n - 1))
    if r > 0.8 and n > 1:
        h = s[:n // 2]
        s = h + (s[n // 2] if n % 2 else '') + h[::-1]
    return s + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1339 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
