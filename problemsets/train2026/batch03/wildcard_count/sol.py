import sys

def sol(inp):
    s, p = inp.split()[:2]
    n, m = len(s), len(p)
    mask = {}
    for i, c in enumerate(s):
        mask[c] = mask.get(c, 0) | (1 << i)
    full = (1 << (n - m + 1)) - 1
    res = full
    for j, c in enumerate(p):
        if c != '?':
            res &= mask.get(c, 0) >> j
    return str(bin(res & full).count('1'))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
