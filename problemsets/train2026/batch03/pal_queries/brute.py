import sys

def brute(inp):
    a = inp.split()
    s = a[0]
    q = int(a[1])
    out = []
    for i in range(q):
        l = int(a[2 + 2 * i]) - 1
        r = int(a[3 + 2 * i])
        t = s[l:r]
        out.append('YES' if t == t[::-1] else 'NO')
    return '\n'.join(out)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
