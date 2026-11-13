import sys

def sol(inp):
    a, b = inp.split()[:2]
    x = [int(t) for t in a.split('.')]
    y = [int(t) for t in b.split('.')]
    for i in range(max(len(x), len(y))):
        u = x[i] if i < len(x) else 0
        v = y[i] if i < len(y) else 0
        if u != v:
            return '-1' if u < v else '1'
    return '0'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
