import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 6 else 'abc'
    h = ''.join(rnd.choice(al) for _ in range(n // 2))
    s = h + rnd.choice(['', 'a']) + h[::-1]
    s = s[:max(1, n - rnd.randint(0, min(3, n - 1)))] if k else s
    tail = ''.join(rnd.choice(al) for _ in range(max(0, n - len(s))))
    s = (s + tail)[:n] or 'a'
    return s + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1334 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
