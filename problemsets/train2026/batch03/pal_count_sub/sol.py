import sys

def sol(inp):
    s = inp.split()[0]
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
    return str(sum((x + 1) // 2 for x in p))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
