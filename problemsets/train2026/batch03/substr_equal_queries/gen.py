import random, sys

def gen(n, rnd, k):
    al = 'ab' if k < 8 else 'abc'
    p = rnd.randint(1, 4)
    base = ''.join(rnd.choice(al) for _ in range(p))
    s = list((base * (n // p + 1))[:n])
    for _ in range(max(1, n // 50)):
        s[rnd.randrange(n)] = rnd.choice(al)
    s = ''.join(s)
    q = n if k else 6
    q = min(q, 100000)
    out = [s, str(q)]
    for _ in range(q):
        l1 = rnd.randrange(n)
        r1 = rnd.randrange(l1, min(n, l1 + (4 if k < 7 else 30)))
        ln = r1 - l1 + 1
        if rnd.random() < 0.6:
            l2 = rnd.randrange(0, n - ln + 1)
            r2 = l2 + ln - 1
            if rnd.random() < 0.7 and l1 + p + ln <= n:
                l2 = l1 + p * rnd.randint(1, max(1, (n - l1 - ln) // p))
                l2 = min(l2, n - ln)
                r2 = l2 + ln - 1
        else:
            l2 = rnd.randrange(n)
            r2 = rnd.randrange(l2, min(n, l2 + 5))
        out.append('%d %d %d %d' % (l1 + 1, r1 + 1, l2 + 1, r2 + 1))
    return '\n'.join(out) + '\n'


SIZES = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1389 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
