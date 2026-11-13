import sys

def brute(inp):
    a, b = inp.split()[:2]
    x = [int(t) for t in a.split('.')]
    y = [int(t) for t in b.split('.')]
    m = max(len(x), len(y))
    x += [0] * (m - len(x))
    y += [0] * (m - len(y))
    return '-1' if x < y else '1' if x > y else '0'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
