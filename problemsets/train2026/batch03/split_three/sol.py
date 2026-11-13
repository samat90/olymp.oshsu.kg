import sys

def sol(inp):
    s = inp.split()[0]
    M = 10 ** 9 + 7
    n = len(s)
    pos = [i for i, c in enumerate(s) if c == '1']
    c = len(pos)
    if c % 3:
        return '0'
    if c == 0:
        return str((n - 1) * (n - 2) // 2 % M)
    t = c // 3
    w1 = pos[t] - pos[t - 1]
    w2 = pos[2 * t] - pos[2 * t - 1]
    return str(w1 * w2 % M)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
