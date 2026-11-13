import sys

def brute(inp):
    a = inp.split()
    s = a[0]
    q = int(a[1])
    out = []
    for i in range(q):
        l1, r1, l2, r2 = (int(x) for x in a[2 + 4 * i:6 + 4 * i])
        out.append('YES' if s[l1 - 1:r1] == s[l2 - 1:r2] else 'NO')
    return '\n'.join(out)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
