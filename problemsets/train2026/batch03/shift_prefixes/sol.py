import sys

def sol(inp):
    a = inp.split()
    s = a[0]
    n = len(s)
    x = [int(t) for t in a[1:n + 1]]
    tot = 0
    res = [''] * n
    for i in range(n - 1, -1, -1):
        tot = (tot + x[i]) % 26
        res[i] = chr((ord(s[i]) - 97 + tot) % 26 + 97)
    return ''.join(res)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
