import sys

def sol(inp):
    a, b = inp.split()[:2]
    x = [int(c) for c in reversed(a)]
    y = [int(c) for c in reversed(b)]
    r = [0] * (len(x) + len(y) + 1)
    for i, u in enumerate(x):
        if u:
            for j, v in enumerate(y):
                r[i + j] += u * v
    c = 0
    for i in range(len(r)):
        c += r[i]
        r[i] = c % 10
        c //= 10
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return ''.join(map(str, reversed(r)))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
