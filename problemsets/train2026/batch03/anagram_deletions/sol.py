import sys

def sol(inp):
    a, b = inp.split()[:2]
    from collections import Counter
    x, y = Counter(a), Counter(b)
    return str(sum(abs(x[c] - y[c]) for c in set(x) | set(y)))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
