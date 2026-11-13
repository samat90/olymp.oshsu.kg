import sys

def sol(inp):
    a = inp.split()
    s = a[0]
    q = int(a[1])
    M = (1 << 61) - 1
    B = 911382323 + 972663749
    n = len(s)
    h = [0] * (n + 1)
    pw = [1] * (n + 1)
    for i, c in enumerate(s):
        h[i + 1] = (h[i] * B + ord(c)) % M
        pw[i + 1] = pw[i] * B % M
    out = []
    for i in range(q):
        l1, r1, l2, r2 = (int(x) for x in a[2 + 4 * i:6 + 4 * i])
        if r1 - l1 != r2 - l2:
            out.append('NO')
            continue
        ln = r1 - l1 + 1
        x = (h[r1] - h[l1 - 1] * pw[ln]) % M
        y = (h[r2] - h[l2 - 1] * pw[ln]) % M
        out.append('YES' if x == y else 'NO')
    return '\n'.join(out)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
