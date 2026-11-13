import sys

def brute(inp):
    a, b = inp.split()[:2]
    f, g = {}, {}
    for x, y in zip(a, b):
        if f.get(x, y) != y or g.get(y, x) != x:
            return 'NO'
        f[x] = y
        g[y] = x
    return 'YES'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
