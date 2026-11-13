import sys

def sol(inp):
    a = inp.split()
    r = int(a[0])
    s = a[1]
    if r == 1:
        return s
    rows = [[] for _ in range(r)]
    i, d = 0, 1
    for c in s:
        rows[i].append(c)
        if i == 0:
            d = 1
        elif i == r - 1:
            d = -1
        i += d
    return ''.join(''.join(x) for x in rows)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
