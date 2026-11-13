import sys

def sol(inp):
    a, b = inp.split()[:2]

    def canon(x):
        d = {}
        return [d.setdefault(c, len(d)) for c in x]
    return 'YES' if canon(a) == canon(b) else 'NO'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
