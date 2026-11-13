import random, sys

def gen(n, rnd, k):
    out = []
    o = 0
    for i in range(n):
        left = n - i
        if o == left:
            out.append(')')
            o -= 1
            continue
        r = rnd.random()
        if r < 0.15 and left > o + 1:
            out.append('(')
            o += 1
        elif r < 0.3 and o:
            out.append(')')
            o -= 1
        else:
            out.append(rnd.choice('abcdef'))
    s = ''.join(out)
    return (s if any(c.isalpha() for c in s) else 'a' + s) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1398 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
