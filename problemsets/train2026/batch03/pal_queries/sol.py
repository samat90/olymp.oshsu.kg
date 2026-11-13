import sys

def sol(inp):
    a = inp.split()
    s = a[0]
    q = int(a[1])
    t = '^#' + '#'.join(s) + '#$'
    n = len(t)
    p = [0] * n
    c = r = 0
    for i in range(1, n - 1):
        if i < r:
            p[i] = min(r - i, p[2 * c - i])
        while t[i + 1 + p[i]] == t[i - 1 - p[i]]:
            p[i] += 1
        if i + p[i] > r:
            c, r = i, i + p[i]
    out = []
    for i in range(q):
        l = int(a[2 + 2 * i]) - 1
        rr = int(a[3 + 2 * i]) - 1
        out.append('YES' if p[l + rr + 2] >= rr - l + 1 else 'NO')
    return '\n'.join(out)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
