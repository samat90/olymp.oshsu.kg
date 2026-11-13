import sys

def brute(inp):
    n, k = map(int, inp.split()[:2])
    res = []

    def go(s, o, c):
        if len(s) == 2 * n:
            res.append(s)
            return
        if o < n:
            go(s + '(', o + 1, c)
        if c < o:
            go(s + ')', o, c + 1)
    go('', 0, 0)
    res.sort()
    return res[k - 1] if k <= len(res) else '-1'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
