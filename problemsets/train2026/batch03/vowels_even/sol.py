import sys

def sol(inp):
    s = inp.split()[0]
    bit = {'a': 1, 'e': 2, 'i': 4, 'o': 8, 'u': 16}
    first = {0: -1}
    m = 0
    best = 0
    for i, c in enumerate(s):
        m ^= bit.get(c, 0)
        if m in first:
            best = max(best, i - first[m])
        else:
            first[m] = i
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
