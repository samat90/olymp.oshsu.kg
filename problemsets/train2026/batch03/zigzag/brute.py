import sys

def brute(inp):
    a = inp.split()
    r = int(a[0])
    s = a[1]
    if r == 1:
        return s
    per = 2 * (r - 1)
    res = []
    for row in range(r):
        for i, c in enumerate(s):
            m = i % per
            if min(m, per - m) == row:
                res.append(c)
    return ''.join(res)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
