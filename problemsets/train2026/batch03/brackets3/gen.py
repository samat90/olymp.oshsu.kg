import random, sys

def gen(n, rnd, k):
    pairs = ['()', '[]', '{}']
    st = []
    out = []
    for i in range(n):
        if st and (rnd.random() < 0.5 or len(st) >= n - i):
            out.append(st.pop())
        else:
            p = rnd.choice(pairs)
            out.append(p[0])
            st.append(p[1])
    while st:
        out.append(st.pop())
    if rnd.random() < 0.5:
        out[rnd.randrange(len(out))] = rnd.choice('()[]{}')
    return ''.join(out) + '\n'


SIZES = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]

if __name__ == "__main__":
    k = int(sys.argv[1])
    rnd = random.Random(1390 * 1000 + k)
    sys.stdout.write(gen(SIZES[k - 1], rnd, k))
