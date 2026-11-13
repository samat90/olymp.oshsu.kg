import sys

def sol(inp):
    x = inp.split()[0]
    n = len(x)
    if all(c == '9' for c in x):
        return '1' + '0' * (n - 1) + '1'
    h = (n + 1) // 2
    left = x[:h]

    def mk(l):
        return l + l[:n // 2][::-1]
    c = mk(left)
    if c > x:
        return c
    d = list(left)
    i = len(d) - 1
    while d[i] == '9':
        d[i] = '0'
        i -= 1
    d[i] = chr(ord(d[i]) + 1)
    return mk(''.join(d))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
