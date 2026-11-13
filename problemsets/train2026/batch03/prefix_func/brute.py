import sys

def brute(inp):
    s = inp.split()[0]
    res = []
    for i in range(1, len(s) + 1):
        t = s[:i]
        best = 0
        for l in range(1, i):
            if t[:l] == t[i - l:]:
                best = l
        res.append(best)
    return ' '.join(map(str, res))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
