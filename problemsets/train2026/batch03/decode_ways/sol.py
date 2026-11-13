import sys

def sol(inp):
    s = inp.split()[0]
    M = 10 ** 9 + 7
    a, b = 1, 0
    for i, c in enumerate(s):
        cur = 0
        if c != '0':
            cur += a
        if i and s[i - 1] != '0' and int(s[i - 1:i + 1]) <= 26:
            cur += b
        cur %= M
        a, b = cur, a
    return str(a % M)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
