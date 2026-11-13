import random, sys

def gen(n, rnd, k):
    import sys
    sys.setrecursionlimit(10000)
    mx = 3 if k == 0 else 9

    def ex(b):
        out = []
        while b > 0:
            if b >= 5 and rnd.random() < 0.4:
                inner = rnd.randint(1, min(b - 4, max(1, b // 2)))
                out.append(str(rnd.randint(1, mx)) + '[' + ex(inner) + ']')
                b -= inner + 3
            else:
                out.append(rnd.choice('abc'))
                b -= 1
        return ''.join(out)
    if k >= 5:
        parts = []
        tot = 0
        while tot < n:
            seg = min(n - tot, rnd.randint(5, 200))
            s = ex(seg)
            parts.append(s)
            tot += len(s) + 1
        s = ''.join(parts)
    else:
        s = ex(n)
    return (s or 'a') + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1397 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
