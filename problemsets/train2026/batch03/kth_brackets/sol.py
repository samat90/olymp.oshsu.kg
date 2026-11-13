import sys

def sol(inp):
    n, k = map(int, inp.split()[:2])
    # f[r][o]: ways to finish with r chars left and o open
    f = [[0] * (n + 2) for _ in range(2 * n + 1)]
    f[0][0] = 1
    for r in range(1, 2 * n + 1):
        for o in range(0, n + 1):
            v = f[r - 1][o + 1] if o + 1 <= n else 0
            if o > 0:
                v += f[r - 1][o - 1]
            f[r][o] = v
    if f[2 * n][0] < k:
        return '-1'
    res = []
    o = 0
    for i in range(2 * n):
        r = 2 * n - i - 1
        # try '('
        if o + 1 <= n and f[r][o + 1] >= k:
            res.append('(')
            o += 1
        else:
            if o + 1 <= n:
                k -= f[r][o + 1]
            res.append(')')
            o -= 1
    return ''.join(res)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
