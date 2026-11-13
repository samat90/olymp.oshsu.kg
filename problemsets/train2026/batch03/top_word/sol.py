import sys

def sol(inp):
    a = inp.split()
    n = int(a[0])
    from collections import Counter
    c = Counter(a[1:n + 1])
    w = min(c, key=lambda x: (-c[x], x))
    return '%s %d' % (w, c[w])


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
