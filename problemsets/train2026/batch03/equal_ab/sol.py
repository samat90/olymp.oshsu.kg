import sys

def sol(inp):
    s = inp.split()[0]
    first = {0: -1}
    d = 0
    best = 0
    for i, c in enumerate(s):
        if c == 'a':
            d += 1
        elif c == 'b':
            d -= 1
        if d in first:
            best = max(best, i - first[d])
        else:
            first[d] = i
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
