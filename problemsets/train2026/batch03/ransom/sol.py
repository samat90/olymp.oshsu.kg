import sys

def sol(inp):
    a, b = inp.split()[:2]
    from collections import Counter
    x, y = Counter(a), Counter(b)
    return 'YES' if all(y[c] >= v for c, v in x.items()) else 'NO'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
